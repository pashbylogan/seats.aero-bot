#!/usr/bin/env python3
"""
Seats.aero Flight Finder

A script to find the cheapest award flights using the seats.aero API.
Searches for one-way flights based on configuration in a YAML file.
"""

import argparse
import sys
from datetime import datetime
from typing import Any

import requests
import yaml
from tabulate import tabulate

from credit_cards import (
    get_credit_card_name,
    get_transfer_partners,
    list_all_credit_cards,
)

# Cache for currency conversion rates
_CURRENCY_RATES_CACHE: dict[str, float] = {}


def get_usd_conversion_rate(currency: str) -> float:
    """
    Get live USD conversion rate for a given currency.

    Args:
        currency: Currency code (e.g., 'CAD', 'EUR', 'GBP')

    Returns:
        Conversion rate to USD (amount in currency * rate = USD)
    """
    if currency == "USD":
        return 1.0

    # Check cache first
    if currency in _CURRENCY_RATES_CACHE:
        return _CURRENCY_RATES_CACHE[currency]

    try:
        # Use exchangerate-api.com free tier (1500 requests/month)
        response = requests.get(
            f"https://api.exchangerate-api.com/v4/latest/{currency}",
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        # Get rate to USD
        rate = data.get("rates", {}).get("USD", 1.0)
        _CURRENCY_RATES_CACHE[currency] = rate
        return rate

    except Exception as e:
        print(
            f"Warning: Could not fetch live conversion rate for {currency}: {e}",
            file=sys.stderr,
        )
        # Fallback to approximate rates
        fallback_rates = {
            "CAD": 0.72,
            "EUR": 1.08,
            "GBP": 1.27,
            "JPY": 0.0067,
            "AUD": 0.65,
            "NZD": 0.60,
        }
        return fallback_rates.get(currency, 1.0)


class SeatsAeroClient:
    """Client for interacting with the Seats.aero API."""

    BASE_URL = "https://seats.aero/partnerapi"
    SEARCH_ENDPOINT = f"{BASE_URL}/search"

    def __init__(self, api_key: str):
        """
        Initialize the Seats.aero API client.

        Args:
            api_key: Your seats.aero API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Partner-Authorization": self.api_key, "Accept": "application/json"}
        )

    def search_flights(
        self,
        origin: str,
        destination: str,
        cabin: str,
        start_date: str,
        end_date: str,
        sources: list[str] | None = None,
        take: int = 500,
    ) -> dict[str, Any]:
        """
        Search for award flights using the search endpoint.

        Args:
            origin: Origin airport code(s), comma-separated
            destination: Destination airport code(s), comma-separated
            cabin: Cabin class (economy, business, first)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            sources: Optional list of mileage program sources to filter
            take: Maximum number of results to return (default 500)

        Returns:
            API response as dictionary with flight results
        """
        if not sources:
            print(
                "Error: No mileage programs specified. Use credit_card or sources in config.",
                file=sys.stderr,
            )
            sys.exit(1)

        params = {
            "origin_airport": origin,
            "destination_airport": destination,
            "cabins": cabin,
            "start_date": start_date,
            "end_date": end_date,
            "sources": ",".join(sources),
            "order_by": "lowest_mileage",
            "take": take,
        }

        try:
            response = self.session.get(self.SEARCH_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}", file=sys.stderr)
            if hasattr(e, "response") and e.response is not None:
                print(f"Response status: {e.response.status_code}", file=sys.stderr)
                print(f"Response body: {e.response.text}", file=sys.stderr)
            sys.exit(1)


class FlightResult:
    """Represents a single flight search result."""

    def __init__(self, data: dict[str, Any], cabin: str | None = None):
        """
        Initialize a flight result from API response data.

        Args:
            data: Raw API response data for a single availability
            cabin: Cabin class (economy, premium, business, first)
        """
        self.raw_data = data
        route = data.get("Route", {})
        self.source = route.get("Source", "Unknown")

        # Map cabin to field prefix
        cabin_map = {
            "economy": "Y",
            "premium": "W",
            "business": "J",
            "first": "F",
        }
        prefix = cabin_map.get(cabin, "Y")

        self.miles_cost = data.get(f"{prefix}MileageCostRaw", 0)
        # Taxes are in cents, convert to dollars
        taxes_cents = data.get(f"{prefix}TotalTaxesRaw", 0)
        taxes_in_currency = taxes_cents / 100 if taxes_cents else 0
        original_currency = data.get("TaxesCurrency", "USD")

        # Convert to USD using live rates
        if original_currency != "USD":
            conversion_rate = get_usd_conversion_rate(original_currency)
            self.total_taxes = taxes_in_currency * conversion_rate
            self.taxes_currency = "USD"
        else:
            self.total_taxes = taxes_in_currency
            self.taxes_currency = "USD"

        self.taxes_symbol = "$"
        self.remaining_seats = data.get(f"{prefix}RemainingSeatsRaw", 0)
        self.cabin = cabin or "Unknown"
        self.departs_at = data.get("Date", "")
        self.origin_airport = route.get("OriginAirport", "")
        self.destination_airport = route.get("DestinationAirport", "")

        # Get cabin-specific airline info
        self.carriers = data.get(f"{prefix}AirlinesRaw", "")
        self.flight_numbers = ""  # Not available in summary format
        self.arrives_at = ""  # Not available in summary format
        self.segments = []  # Not available in summary format

        # Determine if direct flight
        is_direct = data.get(f"{prefix}DirectRaw", False)
        self.stops = (
            0 if is_direct else 1
        )  # Simplified - actual stop count not available
        self.total_duration = 0  # Not available in summary format

    def calculate_cpp(self, cash_price: float | None = None) -> float | None:
        """
        Calculate cents per point (CPP).

        CPP = (Cash Price - Taxes) / Miles * 100

        Args:
            cash_price: Cash price of the flight in USD

        Returns:
            CPP value or None if cash price not provided
        """
        if cash_price is None or self.miles_cost == 0:
            return None

        # Convert taxes to USD if needed (simplified - assumes same currency)
        taxes_usd = self.total_taxes

        cpp = ((cash_price - taxes_usd) / self.miles_cost) * 100
        return round(cpp, 2)

    def format_duration(self) -> str:
        """Format flight duration in hours and minutes."""
        if not self.total_duration:
            return "N/A"

        hours = self.total_duration // 60
        minutes = self.total_duration % 60
        return f"{hours}h {minutes}m"

    def format_datetime(self, dt_string: str) -> str:
        """Format ISO datetime string to readable format."""
        if not dt_string:
            return "N/A"

        try:
            dt = datetime.fromisoformat(dt_string.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, AttributeError):
            return dt_string

    def format_stops(self) -> str:
        """Format number of stops."""
        if self.stops == 0:
            return "Nonstop"
        elif self.stops == 1:
            return "1 stop"
        else:
            return f"{self.stops} stops"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for display."""
        result = {
            "Program": self.source,
            "Date": self.format_datetime(self.departs_at) if self.departs_at else "N/A",
            "Miles": f"{self.miles_cost:,}",
            "Taxes": f"{self.taxes_symbol}{self.total_taxes:.2f}",
            "Seats": self.remaining_seats,
            "Cabin": self.cabin.title(),
        }

        # Add route information
        if self.origin_airport and self.destination_airport:
            result["Route"] = f"{self.origin_airport} → {self.destination_airport}"

        # Add detailed fields if available (from detailed search)
        if self.arrives_at:
            result["Arrival"] = self.format_datetime(self.arrives_at)
        if self.total_duration:
            result["Duration"] = self.format_duration()
        if self.flight_numbers:
            result["Flights"] = self.flight_numbers
        else:
            result["Stops"] = self.format_stops()

        return result


class FlightFinder:
    """Main application for finding flights."""

    def __init__(self, config_path: str):
        """
        Initialize the flight finder.

        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self.load_config(config_path)
        self.client = SeatsAeroClient(self.config["api_key"])

    @staticmethod
    def load_config(config_path: str) -> dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to configuration file

        Returns:
            Configuration dictionary
        """
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
                return config
        except FileNotFoundError:
            print(
                f"Error: Configuration file not found: {config_path}", file=sys.stderr
            )
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Error parsing YAML configuration: {e}", file=sys.stderr)
            sys.exit(1)

    def search(self) -> list[FlightResult]:
        """
        Perform flight search based on configuration.

        Returns:
            List of flight results
        """
        search_config = self.config["search"]

        # Determine which sources to search
        sources = None
        if search_config.get("credit_card"):
            # Use credit card transfer partners
            credit_card = search_config["credit_card"]
            try:
                sources = get_transfer_partners(credit_card)
                credit_card_name = get_credit_card_name(credit_card)
                print("Searching for flights...")
                print(
                    f"  Route: {search_config['origin']} → {search_config['destination']}"
                )
                print(
                    f"  Dates: {search_config['start_date']} to {search_config['end_date']}"
                )
                print(f"  Cabin: {search_config['cabin']}")
                print(f"  Credit Card: {credit_card_name}")
                print(f"  Transfer Partners: {len(sources)} programs\n")
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                print(
                    f"Available credit cards: {', '.join(list_all_credit_cards())}",
                    file=sys.stderr,
                )
                sys.exit(1)
        elif search_config.get("sources"):
            # Use manually specified sources
            sources = search_config["sources"]
            print("Searching for flights using bulk availability...")
            print(
                f"  Route: {search_config['origin']} → {search_config['destination']}"
            )
            print(
                f"  Dates: {search_config['start_date']} to {search_config['end_date']}"
            )
            print(f"  Cabin: {search_config['cabin']}")
            print(f"  Programs: {', '.join(sources)}\n")
        else:
            print(
                "Error: No mileage programs specified. Use credit_card or sources in config.",
                file=sys.stderr,
            )
            sys.exit(1)

        response = self.client.search_flights(
            origin=search_config["origin"],
            destination=search_config["destination"],
            cabin=search_config["cabin"],
            start_date=search_config["start_date"],
            end_date=search_config["end_date"],
            sources=sources,
        )

        # Parse results
        results = []
        data_list = response.get("data", [])

        if not data_list:
            print("No flights found for the given criteria.")
            return []

        for item in data_list:
            results.append(FlightResult(item, cabin=search_config["cabin"]))

        return results

    def filter_results(self, results: list[FlightResult]) -> list[FlightResult]:
        """
        Filter results based on configuration.

        Args:
            results: List of flight results

        Returns:
            Filtered list of results
        """
        filtered = results
        output_config = self.config.get("output", {})

        # Filter nonstop only
        if output_config.get("nonstop_only", False):
            filtered = [r for r in filtered if r.stops == 0]

        return filtered

    def sort_results(self, results: list[FlightResult]) -> list[FlightResult]:
        """
        Sort results based on configuration.

        Args:
            results: List of flight results

        Returns:
            Sorted list of results
        """
        output_config = self.config.get("output", {})
        sort_by = output_config.get("sort_by", "total_cost")

        if sort_by == "miles":
            # Sort by miles, then by taxes as tiebreaker
            return sorted(results, key=lambda x: (x.miles_cost, x.total_taxes))
        elif sort_by == "total_cost":
            # Sort by total cost (1 point = 1 cent, so miles/100 + taxes in USD)
            return sorted(results, key=lambda x: (x.miles_cost / 100) + x.total_taxes)
        elif sort_by == "cpp":
            # Sort by CPP (highest first) - requires cash price
            cash_price = self.config.get("valuation", {}).get("baseline_cash_price")
            if cash_price:
                return sorted(
                    results,
                    key=lambda x: x.calculate_cpp(cash_price) or 0,
                    reverse=True,
                )
            else:
                print(
                    "Warning: Cannot sort by CPP without baseline_cash_price. Sorting by total cost instead."
                )
                return sorted(results, key=lambda x: x.miles_cost + x.total_taxes)
        elif sort_by == "date":
            return sorted(results, key=lambda x: x.departs_at)
        else:
            return results

    def display_results(self, results: list[FlightResult]):
        """
        Display search results.

        Args:
            results: List of flight results to display
        """
        search_config = self.config["search"]
        max_results = search_config.get("max_results", 10)
        output_config = self.config.get("output", {})
        valuation_config = self.config.get("valuation", {})

        # Limit results
        displayed_results = results[:max_results]

        print(f"Found {len(results)} flights. Showing top {len(displayed_results)}:\n")

        # Prepare table data
        table_data = []
        for i, result in enumerate(displayed_results, 1):
            row = result.to_dict()

            # Add CPP if baseline cash price is provided
            cash_price = valuation_config.get("baseline_cash_price")
            if cash_price:
                cpp = result.calculate_cpp(cash_price)
                if cpp is not None:
                    row["CPP"] = f"{cpp:.2f}¢"
                else:
                    row["CPP"] = "N/A"

            # Add row number
            row = {"#": i, **row}
            table_data.append(row)

        # Display table
        if table_data:
            headers = table_data[0].keys()
            rows = [list(row.values()) for row in table_data]
            print(tabulate(rows, headers=headers, tablefmt="grid"))

        # Display segment details if requested
        if output_config.get("show_segments", False):
            print("\n" + "=" * 80)
            print("FLIGHT DETAILS")
            print("=" * 80)

            for i, result in enumerate(displayed_results, 1):
                print(f"\n[{i}] {result.source} - {result.flight_numbers}")
                print(
                    f"    Cost: {result.miles_cost:,} miles + {result.taxes_symbol}{result.total_taxes:.2f}"
                )

                if result.segments:
                    print("    Segments:")
                    for j, segment in enumerate(result.segments, 1):
                        origin = segment.get("OriginAirport", "???")
                        dest = segment.get("DestinationAirport", "???")
                        flight = segment.get("FlightNumber", "???")
                        depart = result.format_datetime(segment.get("DepartsAt", ""))
                        arrive = result.format_datetime(segment.get("ArrivesAt", ""))
                        aircraft = segment.get("AircraftName", "Unknown")
                        fare_class = segment.get("FareClass", "?")

                        print(f"      {j}. {flight}: {origin} → {dest}")
                        print(f"         Departs: {depart} | Arrives: {arrive}")
                        print(
                            f"         Aircraft: {aircraft} | Fare Class: {fare_class}"
                        )

    def run(self):
        """Run the flight finder application."""
        # Search for flights
        results = self.search()

        if not results:
            return

        # Filter results
        results = self.filter_results(results)

        # Sort results
        results = self.sort_results(results)

        # Display results
        self.display_results(results)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Find the cheapest award flights using seats.aero API"
    )
    parser.add_argument(
        "-c",
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)",
    )

    args = parser.parse_args()

    try:
        finder = FlightFinder(args.config)
        finder.run()
    except KeyboardInterrupt:
        print("\n\nSearch cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
