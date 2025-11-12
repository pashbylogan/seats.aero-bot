"""
Credit card transfer partner mappings for seats.aero loyalty programs.

This module maps major credit card rewards programs to their airline and hotel
transfer partners, along with the corresponding seats.aero source identifiers.
"""

from enum import Enum


class CreditCard(Enum):
    """Supported credit card programs."""
    CAPITAL_ONE = "capital-one"
    CHASE = "chase"
    AMEX = "amex"
    CITI = "citi"
    BILT = "bilt"

    @property
    def display_name(self) -> str:
        """Get the friendly display name for this credit card."""
        return _CREDIT_CARD_INFO[self]["name"]

    @property
    def airline_partners(self) -> list[str]:
        """Get the list of airline transfer partners for this credit card."""
        return _CREDIT_CARD_INFO[self]["airlines"]


class AirlineSource(Enum):
    """Common airline loyalty program source identifiers for seats.aero."""
    AA = "aa"
    AEROPLAN = "aeroplan"
    AEROMEXICO = "aeromexico"
    ALASKA = "alaska"
    ANA = "ana"
    ASIA_MILES = "asia-miles"
    DELTA = "delta"
    ETIHAD = "etihad"
    EXECUTIVE_CLUB = "executive-club"
    FINNAIR = "finnair"
    FLYING_BLUE = "flying-blue"
    HAWAIIAN = "hawaiian"
    JETBLUE = "jetblue"
    KRISFLYER = "krisflyer"
    PRIVILEGE_CLUB = "privilege-club"
    QANTAS = "qantas"
    SKYWARDS = "skywards"
    SOUTHWEST = "southwest"
    TURKISH = "turkish"
    UNITED = "united"
    VIRGIN_ATLANTIC = "virgin-atlantic"

    @property
    def display_name(self) -> str:
        """Get the friendly airline name."""
        return _SOURCE_TO_AIRLINE.get(self.value, self.value)


# Internal mapping of credit card programs to their transfer partners
_CREDIT_CARD_INFO: dict[CreditCard, dict[str, str | list[str]]] = {
    CreditCard.CAPITAL_ONE: {
        "name": "Capital One (Venture, VentureX, Spark Miles)",
        "airlines": [
            "aeroplan",          # Air Canada Aeroplan (1:1)
            # "lifemiles",       # Avianca LifeMiles (1:1) - Note: seats.aero no longer supports LifeMiles
            "executive-club",    # British Airways Executive Club (1:1)
            "asia-miles",        # Cathay Pacific Asia Miles (1:1)
            "skywards",          # Emirates Skywards (1:1)
            "etihad",            # Etihad Guest (1:1)
            "finnair",           # Finnair Plus (1:1)
            "flying-blue",       # Air France-KLM Flying Blue (1:1)
            "qantas",            # Qantas Frequent Flyer (1:1)
            "privilege-club",    # Qatar Airways Privilege Club (1:1)
            "krisflyer",         # Singapore Airlines KrisFlyer (1:1)
            "turkish",           # Turkish Airlines Miles&Smiles (1:1)
            # Note: Capital One also has EVA Air, Japan Airlines, JetBlue, TAP, etc.
            # but not all may be available in seats.aero
        ],
    },
    CreditCard.CHASE: {
        "name": "Chase Ultimate Rewards (Sapphire, Freedom, Ink)",
        "airlines": [
            "aeroplan",          # Air Canada Aeroplan (1:1)
            "executive-club",    # British Airways Executive Club (1:1)
            "flying-blue",       # Air France-KLM Flying Blue (1:1)
            "krisflyer",         # Singapore Airlines KrisFlyer (1:1)
            "united",            # United MileagePlus (1:1)
            "southwest",         # Southwest Rapid Rewards (1:1)
            "jetblue",           # JetBlue TrueBlue (1:1)
            "virgin-atlantic",   # Virgin Atlantic Flying Club (1:1)
            # Also: Iberia Plus, but may not be in seats.aero
        ],
    },
    CreditCard.AMEX: {
        "name": "American Express Membership Rewards",
        "airlines": [
            "aeroplan",          # Air Canada Aeroplan (1:1)
            "aeromexico",        # Aeromexico Club Premier (1:1)
            "ana",               # ANA Mileage Club (1:1)
            "asia-miles",        # Cathay Pacific Asia Miles (1:1)
            "delta",             # Delta SkyMiles (1:1)
            "skywards",          # Emirates Skywards (1:1)
            "etihad",            # Etihad Guest (1:1)
            "finnair",           # Finnair Plus (1:1)
            "flying-blue",       # Air France-KLM Flying Blue (1:1)
            "hawaiian",          # Hawaiian Airlines HawaiianMiles (1:1)
            "jetblue",           # JetBlue TrueBlue (1:1)
            "qantas",            # Qantas Frequent Flyer (1:1)
            "krisflyer",         # Singapore Airlines KrisFlyer (1:1)
            "virgin-atlantic",   # Virgin Atlantic Flying Club (1:1)
            # Also: British Airways, Iberia, Avianca, etc.
        ],
    },
    CreditCard.CITI: {
        "name": "Citi ThankYou Rewards (Premier, Prestige, Rewards+)",
        "airlines": [
            "aa",                # American Airlines AAdvantage (1:1)
            "aeroplan",          # Air Canada Aeroplan (1:1)
            "asia-miles",        # Cathay Pacific Asia Miles (1:1)
            "flying-blue",       # Air France-KLM Flying Blue (1:1)
            "jetblue",           # JetBlue TrueBlue (1:1)
            "qantas",            # Qantas Frequent Flyer (1:1)
            "privilege-club",    # Qatar Airways Privilege Club (1:1)
            "krisflyer",         # Singapore Airlines KrisFlyer (1:1)
            "turkish",           # Turkish Airlines Miles&Smiles (1:1)
            "virgin-atlantic",   # Virgin Atlantic Flying Club (1:1)
            # Also: Avianca LifeMiles, EVA Air, etc.
        ],
    },
    CreditCard.BILT: {
        "name": "Bilt Rewards",
        "airlines": [
            "aa",                # American Airlines AAdvantage (1:1)
            "aeroplan",          # Air Canada Aeroplan (1:1)
            "alaska",            # Alaska Airlines Mileage Plan (1:1)
            "executive-club",    # British Airways Executive Club (1:1)
            "asia-miles",        # Cathay Pacific Asia Miles (1:1)
            "flying-blue",       # Air France-KLM Flying Blue (1:1)
            "hawaiian",          # Hawaiian Airlines HawaiianMiles (1:1)
            "turkish",           # Turkish Airlines Miles&Smiles (1:1)
            "united",            # United MileagePlus (1:1)
            "virgin-atlantic",   # Virgin Atlantic Flying Club (1:1)
        ],
    },
}

# Reverse mapping: seats.aero source to friendly airline name
_SOURCE_TO_AIRLINE: dict[str, str] = {
    "aa": "American Airlines AAdvantage",
    "aeroplan": "Air Canada Aeroplan",
    "aeromexico": "Aeromexico Club Premier",
    "alaska": "Alaska Airlines Mileage Plan",
    "ana": "ANA Mileage Club",
    "asia-miles": "Cathay Pacific Asia Miles",
    "delta": "Delta SkyMiles",
    "etihad": "Etihad Guest",
    "executive-club": "British Airways Executive Club",
    "finnair": "Finnair Plus",
    "flying-blue": "Air France-KLM Flying Blue",
    "hawaiian": "Hawaiian Airlines HawaiianMiles",
    "jetblue": "JetBlue TrueBlue",
    "krisflyer": "Singapore Airlines KrisFlyer",
    "privilege-club": "Qatar Airways Privilege Club",
    "qantas": "Qantas Frequent Flyer",
    "skywards": "Emirates Skywards",
    "southwest": "Southwest Rapid Rewards",
    "turkish": "Turkish Airlines Miles&Smiles",
    "united": "United MileagePlus",
    "virgin-atlantic": "Virgin Atlantic Flying Club",
}


def get_transfer_partners(credit_card: str) -> list[str]:
    """
    Get the list of airline transfer partners for a given credit card.

    Args:
        credit_card: Credit card identifier (e.g., 'capital-one', 'chase', 'amex', 'citi', 'bilt')

    Returns:
        List of seats.aero source identifiers for the card's transfer partners

    Raises:
        ValueError: If credit card is not recognized
    """
    # Try to match by enum value
    try:
        card = CreditCard(credit_card.lower())
        return card.airline_partners
    except ValueError:
        available = ", ".join(card.value for card in CreditCard)
        raise ValueError(
            f"Unknown credit card: '{credit_card}'. "
            f"Available options: {available}"
        ) from None


def get_credit_card_name(credit_card: str) -> str:
    """Get the friendly name for a credit card program."""
    try:
        card = CreditCard(credit_card.lower())
        return card.display_name
    except ValueError:
        return credit_card


def list_all_credit_cards() -> list[str]:
    """Get a list of all supported credit card identifiers."""
    return [card.value for card in CreditCard]


def get_airline_name(source: str) -> str:
    """Get the friendly airline name for a seats.aero source."""
    return _SOURCE_TO_AIRLINE.get(source, source)

