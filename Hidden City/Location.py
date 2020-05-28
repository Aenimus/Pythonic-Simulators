import random
from typing import Dict, List, Optional, TYPE_CHECKING, TypeVar
from functools import cached_property
from dataclasses import dataclass, field

import utils
if TYPE_CHECKING:
    from PlayerState import PlayerState
from Encounter import Encounter, Superlikely, Combat, NonCombat, tumbleweed

T = TypeVar('T')
def weighted_random(weights: Dict[T, int]) -> Optional[T]:
    total = sum(weight for weight in weights.values())
    if total == 0:
        return None
    r = random.randint(1, total)
    for (item, weight) in weights.items():
        r -= weight
        if r <= 0:
            return item


@dataclass(frozen=True)
class Location:
    name: str
    nc: int = 0
    encounters: Optional[List[Encounter]] = field(default_factory=list, hash=False)

    @cached_property
    def superlikelies(self) -> List[Superlikely]:
        return [e for e in self.encounters if isinstance(e, Superlikely)]

    @cached_property
    def non_combats(self) -> List[NonCombat]:
        return [e for e in self.encounters if isinstance(e, NonCombat)]
    
    @cached_property
    def combats(self) -> List[Combat]:
        return [e for e in self.encounters if isinstance(e, Combat)]

    def __str__(self) -> str:
        return self.name

    def select_superlikely(self, player_state: "PlayerState") -> Optional["Superlikely"]:
        sls = [s for s in self.superlikelies if s.validate(player_state, self)]
        if sls:
            return random.choice(self.superlikelies)
        return None

    # Encounter selection
    def select_encounter(self, player_state: "PlayerState") -> "Encounter":
        return self.select_superlikely(player_state) or self.select_nc(player_state) or self.select_combat(player_state)

    def get_nc_weights(self, player_state: "PlayerState") -> Dict:
        nc_weights = {}
        for potential_nc in self.non_combats:
            if potential_nc.validate(player_state, self):
                copies = 1 # I have not sorted the ability for other copies
                if potential_nc not in player_state.locations[self].nc_history:
                    copies = 4 * copies
                nc_weights[potential_nc] = copies #name
        return nc_weights

    def select_nc(self, player_state: "PlayerState") -> Optional["NonCombat"]:
        if not self.non_combats:
            return None
        actual_nc = self.nc + player_state.nc_mod
        if actual_nc < 1:
            return None
        if random.randrange(100) > actual_nc:
            return None
        if len(self.non_combats) > 1:
            potential_nc = weighted_random(self.get_nc_weights(player_state))
            for nc in self.non_combats:
                if nc.name == potential_nc:
                    return nc
        else:
            return self.non_combats[0]
        return None

    def get_combat_weights(self, player_state: "PlayerState", macrod_monster: Optional["Combat"] = None) -> Dict["Combat", int]:
        combat_weights = {}
        for monster in self.combats:
            if monster.validate(player_state, self) is False:
                continue
            if monster is macrod_monster:
                continue

            copies = 1
            if monster not in combat_weights:
                copies += player_state.get_extra_copies(monster)
            if (macrod_monster is None) and ((monster not in player_state.locations[self].combat_history) or player_state.olfacted_monster is monster):
                copies = 4 * copies
            combat_weights[monster] = copies
        return combat_weights

    def select_combat(self, player_state: "PlayerState") -> "Combat":
        weights = self.get_combat_weights(player_state)
        selected = None
        loop = 0
        
        while selected is None and loop < 100:
            selected = weighted_random(weights)

        return selected or tumbleweed

    def select_macro_combat(self, player_state: "PlayerState", original_monster: "Combat") -> "Combat":
        weights = self.get_combat_weights(player_state, original_monster)
        potential_combat = weighted_random(weights) # Ignores rejection
        return next((combat for combat in self.combats if combat is potential_combat), tumbleweed)

    def resolve_macro(self, player_state: "PlayerState", original_monster: "Combat") -> None:
        player_state.macro_active = True
        new_monster = self.select_macro_combat(player_state, original_monster)
        player_state.locations[self].macros_used += 1
        player_state.available_macros -= 1
        utils.vlog(f"{player_state.total_turns_spent + 1}: using Macrometeorite on {utils.agreement(original_monster)} {original_monster.name}, which changed it into a {new_monster.name}.")
        new_monster.run_from(4, player_state, self)

    def resolve_turn(self, player_state: "PlayerState")-> None:
        player_state.evaluate_cooldowns() # evluates whether banishers and/or copiers have ended
        encounter = self.select_encounter(player_state)
        encounter.run_all(player_state, self)
 
