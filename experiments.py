"""
Set up your experiment configuration here.

Some AI keys for your convenience:
    "rush" - Rush AI
    "sorianrush" - Sorian AI Rush
    "RNGStandard" - RNG Standard AI
    "DalliConstAIKey" - Dalli AI
    "uvesorush" - Uveso Rush AI
    "swarmterror" - Swarm Terror AI

To find the AI key of any given AI, look in the lua/AI/CustomAIs_v2 directory
in the mod files.
"""

from typing import List, NamedTuple


class Ai(NamedTuple):
    name: str
    faction: str
    slot: int
    team: int


class Experiment(NamedTuple):
    map: str
    ais: List[Ai]

experiments = [
    Experiment("SCMP_007", [
        # I am pretty sure a team of 0 means no team.
        Ai("rush", "uef", slot=1, team=0),
        Ai("sorianrush", "random", slot=2, team=0)
    ]),
    Experiment("SCMP_007", [
        Ai("rush", "uef", slot=2, team=0),
        Ai("sorianrush", "random", slot=1, team=0)
    ]),
]

