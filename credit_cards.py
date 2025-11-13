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
    WELLS_FARGO = "wells-fargo"
    ROVE = "rove"

    @property
    def display_name(self) -> str:
        """Get the friendly display name for this credit card."""
        return _CREDIT_CARD_INFO[self]["name"]

    @property
    def airline_partners(self) -> list[str]:
        """Get the list of airline transfer partners for this credit card."""
        partners: list[AirlineSource] = _CREDIT_CARD_INFO[self]["airlines"]
        return [source.value for source in partners]


class AirlineSource(Enum):
    """Common airline loyalty program source identifiers for seats.aero."""

    AA = "american"
    AEROPLAN = "aeroplan"
    AEROMEXICO = "aeromexico"
    ALASKA = "alaska"
    ANA = "ana"
    ASIA_MILES = "asia-miles"
    DELTA = "delta"
    ETIHAD = "etihad"
    EXECUTIVE_CLUB = "executive-club"
    FINNAIR = "finnair"
    FLYING_BLUE = "flyingblue"
    HAWAIIAN = "hawaiian"
    JETBLUE = "jetblue"
    KRISFLYER = "singapore"
    LUFTHANSA = "lufthansa"
    PRIVILEGE_CLUB = "qatar"
    QANTAS = "qantas"
    SKYWARDS = "emirates"
    SOUTHWEST = "southwest"
    TURKISH = "turkish"
    UNITED = "united"
    VIRGIN_ATLANTIC = "virginatlantic"
    VIRGIN_AUSTRALIA = "velocity"

    @property
    def display_name(self) -> str:
        """Get the friendly airline name."""
        return _SOURCE_TO_AIRLINE.get(self, self.value)


# Internal mapping of credit card programs to their transfer partners
_CREDIT_CARD_INFO: dict[CreditCard, dict[str, str | list[AirlineSource]]] = {
    CreditCard.CAPITAL_ONE: {
        "name": "Capital One (Venture, VentureX, Spark Miles)",
        "airlines": [
            AirlineSource.AEROMEXICO,  # Aeromexico Club Premier
            AirlineSource.AEROPLAN,  # Air Canada Aeroplan
            AirlineSource.FLYING_BLUE,  # Air France-KLM Flying Blue
            AirlineSource.SKYWARDS,  # Emirates Skywards
            AirlineSource.ETIHAD,  # Etihad Guest
            AirlineSource.FINNAIR,  # Finnair Plus
            AirlineSource.JETBLUE,  # JetBlue TrueBlue
            AirlineSource.QANTAS,  # Qantas Frequent Flyer
            AirlineSource.PRIVILEGE_CLUB,  # Qatar Airways Privilege Club
            AirlineSource.KRISFLYER,  # Singapore Airlines KrisFlyer
            AirlineSource.TURKISH,  # Turkish Airlines Miles&Smiles
            AirlineSource.VIRGIN_ATLANTIC,  # Virgin Atlantic Flying Club
        ],
    },
    CreditCard.CHASE: {
        "name": "Chase Ultimate Rewards (Sapphire, Freedom, Ink)",
        "airlines": [
            AirlineSource.AEROPLAN,  # Air Canada Aeroplan
            AirlineSource.FLYING_BLUE,  # Air France-KLM Flying Blue
            AirlineSource.JETBLUE,  # JetBlue TrueBlue
            AirlineSource.KRISFLYER,  # Singapore Airlines KrisFlyer
            AirlineSource.UNITED,  # United MileagePlus
            AirlineSource.VIRGIN_ATLANTIC,  # Virgin Atlantic Flying Club
        ],
    },
    CreditCard.AMEX: {
        "name": "American Express Membership Rewards",
        "airlines": [
            AirlineSource.AEROMEXICO,  # Aeromexico Club Premier
            AirlineSource.AEROPLAN,  # Air Canada Aeroplan
            AirlineSource.FLYING_BLUE,  # Air France-KLM Flying Blue
            AirlineSource.DELTA,  # Delta SkyMiles
            AirlineSource.SKYWARDS,  # Emirates Skywards
            AirlineSource.ETIHAD,  # Etihad Guest
            AirlineSource.JETBLUE,  # JetBlue TrueBlue
            AirlineSource.QANTAS,  # Qantas Frequent Flyer
            AirlineSource.PRIVILEGE_CLUB,  # Qatar Airways Privilege Club
            AirlineSource.KRISFLYER,  # Singapore Airlines KrisFlyer
            AirlineSource.VIRGIN_ATLANTIC,  # Virgin Atlantic Flying Club
            AirlineSource.VIRGIN_AUSTRALIA,  # Virgin Australia Velocity
        ],
    },
    CreditCard.CITI: {
        "name": "Citi ThankYou Rewards (Premier, Prestige, Rewards+)",
        "airlines": [
            AirlineSource.AEROMEXICO,  # Aeromexico Club Premier
            AirlineSource.AA,  # American Airlines AAdvantage
            AirlineSource.FLYING_BLUE,  # Air France-KLM Flying Blue
            AirlineSource.SKYWARDS,  # Emirates Skywards
            AirlineSource.ETIHAD,  # Etihad Guest
            AirlineSource.JETBLUE,  # JetBlue TrueBlue
            AirlineSource.PRIVILEGE_CLUB,  # Qatar Airways Privilege Club
            AirlineSource.KRISFLYER,  # Singapore Airlines KrisFlyer
            AirlineSource.TURKISH,  # Turkish Airlines Miles&Smiles
            AirlineSource.VIRGIN_ATLANTIC,  # Virgin Atlantic Flying Club
        ],
    },
    CreditCard.BILT: {
        "name": "Bilt Rewards",
        "airlines": [
            AirlineSource.AEROPLAN,  # Air Canada Aeroplan
            AirlineSource.FLYING_BLUE,  # Air France-KLM Flying Blue
            AirlineSource.ALASKA,  # Alaska Atmos Rewards
            AirlineSource.SKYWARDS,  # Emirates Skywards
            AirlineSource.ETIHAD,  # Etihad Guest
            AirlineSource.PRIVILEGE_CLUB,  # Qatar Airways Privilege Club
            AirlineSource.TURKISH,  # Turkish Airlines Miles&Smiles
            AirlineSource.UNITED,  # United MileagePlus
            AirlineSource.VIRGIN_ATLANTIC,  # Virgin Atlantic Flying Club
        ],
    },
    CreditCard.WELLS_FARGO: {
        "name": "Wells Fargo Autograph",
        "airlines": [
            AirlineSource.FLYING_BLUE,  # Air France-KLM Flying Blue
            AirlineSource.VIRGIN_ATLANTIC,  # Virgin Atlantic Flying Club
        ],
    },
    CreditCard.ROVE: {
        "name": "Rove",
        "airlines": [
            AirlineSource.AEROMEXICO,  # Aeromexico Club Premier
            AirlineSource.ETIHAD,  # Etihad Guest
            AirlineSource.FINNAIR,  # Finnair Plus
            AirlineSource.LUFTHANSA,  # Lufthansa Miles & More
            AirlineSource.PRIVILEGE_CLUB,  # Qatar Airways Privilege Club
        ],
    },
}

# Reverse mapping: seats.aero source to friendly airline name
_SOURCE_TO_AIRLINE: dict[AirlineSource, str] = {
    AirlineSource.AA: "American Airlines AAdvantage",
    AirlineSource.AEROPLAN: "Air Canada Aeroplan",
    AirlineSource.AEROMEXICO: "Aeromexico Club Premier",
    AirlineSource.ALASKA: "Alaska Airlines Mileage Plan",
    AirlineSource.ANA: "ANA Mileage Club",
    AirlineSource.ASIA_MILES: "Cathay Pacific Asia Miles",
    AirlineSource.DELTA: "Delta SkyMiles",
    AirlineSource.ETIHAD: "Etihad Guest",
    AirlineSource.EXECUTIVE_CLUB: "British Airways Executive Club",
    AirlineSource.FINNAIR: "Finnair Plus",
    AirlineSource.FLYING_BLUE: "Air France-KLM Flying Blue",
    AirlineSource.HAWAIIAN: "Hawaiian Airlines HawaiianMiles",
    AirlineSource.JETBLUE: "JetBlue TrueBlue",
    AirlineSource.KRISFLYER: "Singapore Airlines KrisFlyer",
    AirlineSource.LUFTHANSA: "Lufthansa Miles & More",
    AirlineSource.PRIVILEGE_CLUB: "Qatar Airways Privilege Club",
    AirlineSource.QANTAS: "Qantas Frequent Flyer",
    AirlineSource.SKYWARDS: "Emirates Skywards",
    AirlineSource.SOUTHWEST: "Southwest Rapid Rewards",
    AirlineSource.TURKISH: "Turkish Airlines Miles&Smiles",
    AirlineSource.UNITED: "United MileagePlus",
    AirlineSource.VIRGIN_ATLANTIC: "Virgin Atlantic Flying Club",
    AirlineSource.VIRGIN_AUSTRALIA: "Virgin Australia Velocity",
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
            f"Unknown credit card: '{credit_card}'. Available options: {available}"
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
    try:
        airline = AirlineSource(source)
        return _SOURCE_TO_AIRLINE.get(airline, source)
    except ValueError:
        return source
