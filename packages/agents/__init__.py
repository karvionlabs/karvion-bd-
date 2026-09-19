"""
Agents package for KARVION BD.
Contains specialized agents for handling specific domain queries.
Domains: student, consumer, citizen, farmer, market, waste
"""

from .student import StudentAgent
from .consumer import ConsumerAgent
from .citizen import CitizenAgent
from .farmer import FarmerAgent
from .market import MarketAgent
from .waste import WasteAgent

__all__ = [
    "StudentAgent",
    "ConsumerAgent",
    "CitizenAgent",
    "FarmerAgent",
    "MarketAgent",
    "WasteAgent",
]
