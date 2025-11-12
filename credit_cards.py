"""
Credit card transfer partner mappings for seats.aero loyalty programs.

This module maps major credit card rewards programs to their airline and hotel
transfer partners, along with the corresponding seats.aero source identifiers.
"""

from typing import Dict, List

# Mapping of credit card programs to their transfer partners
# Format: "credit_card_name": ["seats_aero_source1", "seats_aero_source2", ...]

CREDIT_CARD_PARTNERS: Dict[str, Dict[str, List[str]]] = {
    "capital-one": {
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
        "hotels": [],  # seats.aero focuses on flights
    },

    "chase": {
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
        "hotels": [],
    },

    "amex": {
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
        "hotels": [],
    },

    "citi": {
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
        "hotels": [],
    },

    "bilt": {
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
        "hotels": [],
    },
}

# Reverse mapping: seats.aero source to friendly airline name
SOURCE_TO_AIRLINE: Dict[str, str] = {
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


def get_transfer_partners(credit_card: str) -> List[str]:
    """
    Get the list of airline transfer partners for a given credit card.

    Args:
        credit_card: Credit card identifier (e.g., 'capital-one', 'chase', 'amex', 'citi', 'bilt')

    Returns:
        List of seats.aero source identifiers for the card's transfer partners

    Raises:
        ValueError: If credit card is not recognized
    """
    credit_card_lower = credit_card.lower()

    if credit_card_lower not in CREDIT_CARD_PARTNERS:
        available = ", ".join(CREDIT_CARD_PARTNERS.keys())
        raise ValueError(
            f"Unknown credit card: '{credit_card}'. "
            f"Available options: {available}"
        )

    return CREDIT_CARD_PARTNERS[credit_card_lower]["airlines"]


def get_credit_card_name(credit_card: str) -> str:
    """Get the friendly name for a credit card program."""
    credit_card_lower = credit_card.lower()
    if credit_card_lower in CREDIT_CARD_PARTNERS:
        return CREDIT_CARD_PARTNERS[credit_card_lower]["name"]
    return credit_card


def list_all_credit_cards() -> List[str]:
    """Get a list of all supported credit card identifiers."""
    return list(CREDIT_CARD_PARTNERS.keys())


def get_airline_name(source: str) -> str:
    """Get the friendly airline name for a seats.aero source."""
    return SOURCE_TO_AIRLINE.get(source, source)
