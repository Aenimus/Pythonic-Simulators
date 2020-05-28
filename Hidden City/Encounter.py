from dataclasses import dataclass, field
from typing import Dict, Optional, Callable, TYPE_CHECKING
from enum import Enum, auto
import random
import math

import utils
from Items import Items
if TYPE_CHECKING:
    from PlayerState import PlayerState
    from Location import Location
    from Encounter import Encounter


class Phylum(Enum):
    BEAST = auto()
    BUG = auto()
    CONSTELLATION = auto()
    CONSTRUCT = auto()
    DEMON = auto()
    DUDE = auto()
    ELEMENTAL = auto()
    ELF = auto()
    FISH = auto()
    GOBLIN = auto()
    HIPPIE = auto()
    HOBO = auto()
    HORROR = auto()
    HUMANOID = auto()
    MERKIN = auto()
    ORC = auto()
    PENGUIN = auto()
    PIRATE = auto()
    PLANT = auto()
    SLIME = auto()
    UNDEAD = auto()
    WEIRD = auto()

    @classmethod
    def get_name(cls, phylum: "Phylum"):
        name = next(name for name, value in vars(cls).items() if value == phylum)
        name = name[0] + name[1:].lower()
        return name


class EncounterType(Enum):
    NONE = 0
    SL = 1
    NC = 2
    COMBAT = 3

def default_validate(encounter, player_state: "PlayerState", location: "Location", **kwargs) -> bool:
    return player_state.locations[location].turns_spent >= encounter.delay
    

@dataclass(frozen=True)
class Encounter:
    name: str
    delay: int = 0
    validator: Optional[Callable] = default_validate
    run1: Optional[Callable] = None
    run4: Optional[Callable] = None

    def __str__(self)-> str:
        return f"Encounter({self.name})"

    def validate(self, player_state: "PlayerState", location: "Location")-> bool:
        return self.validator(self, player_state, location)

    def spend_turn(self, player_state: "PlayerState", location: "Location")-> None:
        player_state.locations[location].turns_spent += 1
        player_state.total_turns_spent += 1

    def verbose_log(self, player_state: "PlayerState", location: "Location")-> None:
        utils.vlog(f"{player_state.total_turns_spent}: Encountered {self.name} at {player_state.locations[location].progress} location progress.")

    def should_queue(self, player_state: "PlayerState", location: "Location") -> bool:
        if isinstance(self, NonCombat):
            return len(location.non_combats) > 1
        elif isinstance(self, Combat):
            if not player_state.saber_active:
                return len(location.combats) > 1

        return False

    # Beginning of combat stuff
    def run_stage1(self, player_state: "PlayerState", location: "Location")-> None:
        if self.run1 is not None:
            self.run1(self, player_state, location)

    # Queue stuff
    def run_stage2(self, player_state: "PlayerState", location: "Location")-> None:
        pass

    # Encounter-specific post-queue stuff
    def run_stage3(self, player_state: "PlayerState", location: "Location")-> bool:
        return True

    # Encounter-specific post-queue stuff
    def run_stage4(self, player_state: "PlayerState", location: "Location")-> None:
        if self.run4 is not None:
            self.run4(self, player_state, location)

     # General post-encounter stuff
    def run_stage5(self, player_state: "PlayerState", location: "Location")-> None:
        self.spend_turn(player_state, location)

    def run_from(self, step: int, player_state: "PlayerState", location: "Location") -> None:
        kwargs = {"player_state": player_state, "location": location}
        self.verbose_log(**kwargs)
        keep_running = False
        if step <= 1:
            self.run_stage1(**kwargs)
        if step <= 2:
            self.run_stage2(**kwargs)
        if step <= 3:
            keep_running = self.run_stage3(**kwargs)
        if keep_running and step <= 4:
            self.run_stage4(**kwargs)
        if keep_running and step <= 5:
            self.run_stage5(**kwargs)

    def run_all(self, player_state: "PlayerState", location: "Location")-> None:
        self.run_from(1, player_state, location)


@dataclass(frozen=True)
class Superlikely(Encounter):
    def run_stage1(self, player_state: "PlayerState", location: "Location") -> None:
        player_state.locations[location].superlikelies_encountered += 1


@dataclass(frozen=True)
class NonCombat(Encounter):
    def run_stage2(self, player_state: "PlayerState", location: "Location") -> None:
        if self.should_queue:
            self.add_queue(player_state, location)

    def add_queue(self, player_state: "PlayerState", location: "Location") -> None:
        player_state.locations[location].nc_history.append(self)


@dataclass(frozen=True)
class Combat(Encounter):
    phylum: Optional[Phylum] = None
    free: bool = False # This is for permanently free encounters
    group: bool = False
    item_drops: Dict[Items, int] = field(default_factory=dict, hash=False)
    banish_target: bool = False
    copy_target: bool = False
    macro_target: bool = False

    def validate(self, player_state: "PlayerState", location: "Location") -> bool:
        if self.validator(self, player_state, location):
            return all(b.recipient is not self for b in player_state.banishers)
        return False

    def roll_drops(self, player_state: "PlayerState") -> None:
        if self.item_drops:
            for item in self.item_drops:
                roll = random.randrange(100)
                rate = math.floor(self.item_drops[item] * player_state.drop_multiplier)
                if roll < rate:
                    player_state.inventory[item] += 1
                    utils.vlog(f"Acquired {Items.get_name(item)} by rolling {roll} against a total drop rate of {rate}.")
                else:
                    utils.vlog(f"Drop failure: rolled {roll} against a total drop rate of {rate} for {Items.get_name(item)}.")

    def handle_drops(self, player_state: "PlayerState", location: "Location") -> None:
        if player_state.should_roll_drops:
            self.roll_drops(player_state)
        else:
            player_state.should_roll_drops = True

    def should_macro(self, player_state: "PlayerState", location: "Location") -> bool:
        if self not in player_state.decisions.macro_targets:
            return False
        if player_state.available_macros < 1:
            return False
        return player_state.locations[location].macros_used < player_state.decisions.macros_for_location(location)

    def should_banish(self, player_state: "PlayerState", location: "Location") -> bool:
        if self in player_state.decisions.banisher_targets:
            return player_state.locations[location].banishers_used < player_state.decisions.banishers_for_location(location)
        return False  

    def should_copy(self, player_state: "PlayerState", location: "Location") -> bool:
        return self in player_state.decisions.copier_targets

    def is_free(self, player_state) -> bool:
        return self.free or player_state.free_turn

    def resolve_free_turn(self, player_state: "PlayerState", location: "Location") -> None:
        if player_state.free_turn:
            player_state.free_turn = False
            utils.vlog(f"Turn {player_state.total_turns_spent + 1} was a free turn.")

    def add_queue(self, player_state: "PlayerState", location: "Location") -> None:
        player_state.locations[location].combat_history.append(self)

    def run_stage2(self, player_state: "PlayerState", location: "Location") -> None:
        if self.should_queue(player_state, location):
            self.add_queue(player_state, location)

    def run_stage3(self, player_state: "PlayerState", location: "Location") -> bool:
        if self.should_banish(player_state, location): # Banish and copy are mutually exclusive
            player_state.attempt_banisher(location, self)
        elif self.should_copy(player_state, location):
            player_state.attempt_copier(self)
        if player_state.macro_active: # If we macrod the previous combat
            player_state.macro_active = False
        elif self.should_macro(player_state, location):
            location.resolve_macro(player_state, self)
            return False
        return True

    def run_stage5(self, player_state: "PlayerState", location: "Location") -> None:
        # Default is to roll drops; if False, resets back to True.
        self.handle_drops(player_state, location)

        if self.is_free(player_state):
            self.resolve_free_turn(player_state, location)
        else:
            self.spend_turn(player_state, location)


tumbleweed = Combat(name="Tumbleweed", phylum=Phylum.PLANT)
