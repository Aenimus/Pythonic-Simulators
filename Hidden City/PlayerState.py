from dataclasses import dataclass, field
from typing import DefaultDict, Dict, List, Optional, Deque, TYPE_CHECKING
from collections import defaultdict, deque

import utils
from Items import Items, SURGEON_GEAR
from Banisher import Banisher
from Copier import Copier
from typing import Optional, TYPE_CHECKING
if TYPE_CHECKING:
    from Location import Location
    from Encounter import NonCombat, Combat, Phylum


@dataclass
class Decisions:
    banishers_per_location: Dict["Location", int] = field(default_factory=dict)
    macros_per_location: Dict["Location", int] = field(default_factory=dict)
    banisher_targets: List["Combat"] = field(default_factory=list)
    macro_targets: List["Combat"] = field(default_factory=list)
    copier_targets: List["Combat"] = field(default_factory=list)

    def banishers_for_location(self, location: "Location") -> int:
        return self.banishers_per_location.get(location, 0)

    def macros_for_location(self, location: "Location") -> int:
        return self.macros_per_location.get(location, 0)


@dataclass
class LocationState:
    turns_spent: int = 0
    progress: int = 0
    superlikelies_encountered: int = field(init=False, repr=True, default=0)
    nc_history: Deque["NonCombat"] = field(init=False, default=deque([], 5))
    combat_history: Deque["Combat"] = field(init=False, default=deque([], 5))
    banishers_used: int = 0
    macros_used: int = 0

    def increment_progress(self, player_state: "PlayerState", location: "Location", num: int = 1):
        self.progress += num
        utils.vlog(f"Gained {num} progress in {location.name} for a total of {self.progress}.")


@dataclass
class PlayerState:
    decisions: Decisions
    nc_mod: int
    item_mod: int
    total_turns_spent: int = 0
    available_wishes: int = 3
    available_macros: int = 10
    banishers: List[Banisher] = field(default_factory=lambda: Banisher.get_banishers())
    copiers: List[Copier] = field(default_factory=lambda: Copier.get_copiers())
    inventory: DefaultDict[Items, int] = field(default_factory=lambda: defaultdict(int))
    locations: DefaultDict["Location", LocationState] = field(default_factory=lambda: defaultdict(LocationState))
    tracked_phylum: Optional["Phylum"] = None
    olfacted_monster: Optional["Combat"] = None
    latted_monster: Optional["Combat"] = None
    mated_monster: Optional["Combat"] = None
    macro_active: bool = field(init=False, default=False)
    saber_active: bool = field(init=False, default=False)
    free_turn: bool = field(init=False, default=False)
    janitors_moved: bool = field(init=False, default=False)
    accountants_fought: int = field(init=False, default=0)
    cursed_level: int = field(init=False, default=0)
    should_roll_drops: bool = field(init=False, default=True)
    tracking: int = field(init=False, default=0)

    @property
    def surgeonosity(self):
        return sum(self.inventory[gear] > 0 for gear in SURGEON_GEAR)

    @property
    def drop_multiplier(self):
        return 1 + (self.item_mod/ 100)

    def get_extra_copies(self, monster: "Combat"):
        extra_copies = 0
        if monster.phylum == self.tracked_phylum:
            extra_copies = 2
        for copier in self.copiers:
            if copier.recipient == monster:
                extra_copies += copier.copies_created
        return extra_copies

    def attempt_banisher(self, location: "Location", monster: "Combat"):
        for banisher in self.banishers:
            if banisher.validate(self):
                return banisher.use(self, location, monster) # Uses one only

    def attempt_copier(self, monster: "Combat"):
        for copier in self.copiers:
            if copier.recipient != monster.name and copier.validate(self, monster):
                copier.use(self, monster) # Uses them all

    def evaluate_banishers(self):
        for banisher in self.banishers:
            if banisher.recipient and banisher.expiration_turn < self.total_turns_spent:
                banisher.recipient = None
   
    def evaluate_copiers(self):
        for copier in self.copiers:
            if copier.recipient and copier.expiration_turn < self.total_turns_spent:
                if not copier.has_rejection: # If the copier has expired but also grants immunity from rejection, that is also reset
                    self.olfacted_monster = None
                copier.recipient = None
    
    def evaluate_cooldowns(self):
        self.evaluate_copiers()
        self.evaluate_banishers()
