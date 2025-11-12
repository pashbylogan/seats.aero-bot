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
import yaml
import requests
from tabulate import tabulate
from credit_cards import get_transfer_partners, get_credit_card_name, list_all_credit_cards


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
        self.session.headers.update({
            "Partner-Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        })

    def search_flights(
        self,
        origin: str,
        destination: str,
        cabin: str,
        start_date: str,
        end_date: str,
        sources: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Search for award flights.

        Args:
            origin: Origin airport code(s), comma-separated
            destination: Destination airport code(s), comma-separated
            cabin: Cabin class (economy, business, first)
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            sources: Optional list of mileage program sources to filter

        Returns:
            API response as dictionary
        """
        params = {
            "origin": origin,
            "destination": destination,
            "cabin": cabin,
            "departureDate": start_date,
            "returnDate": end_date
        }

        # Add source filter if specified
        if sources:
            params["source"] = ",".join(sources)

        try:
            response = self.session.get(self.SEARCH_ENDPOINT, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making API request: {e}", file=sys.stderr)
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}", file=sys.stderr)
                print(f"Response body: {e.response.text}", file=sys.stderr)
            sys.exit(1)


class FlightResult:
    """Represents a single flight search result."""

    def __init__(self, data: dict[str, Any]):
        """
        Initialize a flight result from API response data.

        Args:
            data: Raw API response data for a single availability
        """
        self.raw_data = data
        self.source = data.get("Source", "Unknown")
        self.miles_cost = data.get("MileageCost", 0)
        self.total_taxes = data.get("TotalTaxes", 0)
        self.taxes_currency = data.get("TaxesCurrency", "USD")
        self.taxes_symbol = data.get("TaxesCurrencySymbol", "$")
        self.remaining_seats = data.get("RemainingSeats", 0)
        self.cabin = data.get("Cabin", "Unknown")
        self.stops = data.get("Stops", 0)
        self.total_duration = data.get("TotalDuration", 0)
        self.carriers = data.get("Carriers", "")
        self.flight_numbers = data.get("FlightNumbers", "")
        self.departs_at = data.get("DepartsAt", "")
        self.arrives_at = data.get("ArrivesAt", "")
        self.segments = data.get("AvailabilitySegments", [])

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
            dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
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
        return {
            "Program": self.source,
            "Departure": self.format_datetime(self.departs_at),
            "Arrival": self.format_datetime(self.arrives_at),
            "Duration": self.format_duration(),
            "Stops": self.format_stops(),
            "Miles": f"{self.miles_cost:,}",
            "Taxes": f"{self.taxes_symbol}{self.total_taxes:.2f}",
            "Seats": self.remaining_seats,
            "Cabin": self.cabin,
            "Flights": self.flight_numbers
        }


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
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config
        except FileNotFoundError:
            print(f"Error: Configuration file not found: {config_path}", file=sys.stderr)
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
                print(f"Searching for flights...")
                print(f"  Route: {search_config['origin']} → {search_config['destination']}")
                print(f"  Dates: {search_config['start_date']} to {search_config['end_date']}")
                print(f"  Cabin: {search_config['cabin']}")
                print(f"  Credit Card: {credit_card_name}")
                print(f"  Transfer Partners: {len(sources)} programs")
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                print(f"Available credit cards: {', '.join(list_all_credit_cards())}", file=sys.stderr)
                sys.exit(1)
        elif search_config.get("sources"):
            # Use manually specified sources
            sources = search_config["sources"]
            print(f"Searching for flights...")
            print(f"  Route: {search_config['origin']} → {search_config['destination']}")
            print(f"  Dates: {search_config['start_date']} to {search_config['end_date']}")
            print(f"  Cabin: {search_config['cabin']}")
            print(f"  Programs: {', '.join(sources)}")
        else:
            # Search all programs
            print(f"Searching for flights...")
            print(f"  Route: {search_config['origin']} → {search_config['destination']}")
            print(f"  Dates: {search_config['start_date']} to {search_config['end_date']}")
            print(f"  Cabin: {search_config['cabin']}")
            print(f"  Programs: All available")

        print()

        response = self.client.search_flights(
            origin=search_config["origin"],
            destination=search_config["destination"],
            cabin=search_config["cabin"],
            start_date=search_config["start_date"],
            end_date=search_config["end_date"],
            sources=sources
        )

        # Parse results
        results = []
        data_list = response.get("data", [])

        if not data_list:
            print("No flights found for the given criteria.")
            return []

        for item in data_list:
            results.append(FlightResult(item))

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
        sort_by = output_config.get("sort_by", "miles")

        if sort_by == "miles":
            return sorted(results, key=lambda x: x.miles_cost)
        elif sort_by == "cpp":
            # Sort by CPP (highest first) - requires cash price
            cash_price = self.config.get("valuation", {}).get("baseline_cash_price")
            if cash_price:
                return sorted(
                    results,
                    key=lambda x: x.calculate_cpp(cash_price) or 0,
                    reverse=True
                )
            else:
                print("Warning: Cannot sort by CPP without baseline_cash_price. Sorting by miles instead.")
                return sorted(results, key=lambda x: x.miles_cost)
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
                print(f"    Cost: {result.miles_cost:,} miles + {result.taxes_symbol}{result.total_taxes:.2f}")

                if result.segments:
                    print(f"    Segments:")
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
                        print(f"         Aircraft: {aircraft} | Fare Class: {fare_class}")

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
        "-c", "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
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
