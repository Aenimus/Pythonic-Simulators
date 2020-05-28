from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import utils
if TYPE_CHECKING:
    from PlayerState import PlayerState
    from Encounter import Combat


@dataclass
class Copier():
    name: str = ""
    turn_duration: int = 30
    max_available_uses: int = 3
    has_cooldown: bool = False
    copies_created: int = 1
    has_rejection: bool = True
    recipient: Optional["Combat"] = field(init=False, repr=True, default=None)
    expiration_turn: int = field(init=False, repr=True, default=-1)

    def validate(self, player_state: "PlayerState", monster: "Combat"):
        if self.recipient == monster:
            return False
        no_cooldown = True
        if self.has_cooldown:
            no_cooldown = self.expiration_turn < player_state.total_turns_spent
        return self.max_available_uses and no_cooldown

    def use(self, player_state: "PlayerState", monster: "Combat"):
        self.recipient = monster
        self.max_available_uses -= 1
        self.expiration_turn = player_state.total_turns_spent + self.turn_duration
        if not self.has_rejection:
            player_state.olfacted_monster = monster # immunity from rejection is handled on player_state while only olfaction does so
        utils.vlog(f"{player_state.total_turns_spent + 1}: Using the copier {self.name} on {utils.agreement(monster)} {monster.name}.")

    @staticmethod
    def get_copiers():
        return [Copier(name="Olfaction", turn_duration=40, max_available_uses=999, has_cooldown=True, copies_created=3, has_rejection=False),
                Copier(name="Share Latte", turn_duration=30, max_available_uses=3, has_cooldown=True, copies_created=2),
                Copier(name="Mating Call", turn_duration=999, max_available_uses=1, has_cooldown=False, copies_created=1)]
