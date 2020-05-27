from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

import utils
if TYPE_CHECKING:
    from PlayerState import PlayerState
    from Location import Location
    from Encounter import Combat


@dataclass
class Banisher:
    name: str = ""
    turn_duration: int = 0
    max_available_uses: int = 3
    has_cooldown: bool = False
    is_free: bool = True
    should_roll_drops: bool = False
    recipient: Optional["Combat"] = field(init=False, repr=True, default=None)
    expiration_turn: int = field(init=False, repr=True, default=-1)

    def validate(self, player_state: "PlayerState"):
        if self.recipient != None:
            return False
        no_cooldown = True
        if self.has_cooldown:
            no_cooldown = self.expiration_turn < player_state.total_turns_spent
        return self.max_available_uses and no_cooldown

    def use(self, player_state: "PlayerState", location: "Location", monster: "Combat"):
        self.recipient = monster
        self.max_available_uses -= 1
        self.expiration_turn = player_state.total_turns_spent + self.turn_duration
        if not self.should_roll_drops:
            player_state.should_roll_drops = False
        if self.is_free:
            player_state.free_turn = True
        player_state.locations[location].banishers_used += 1
        utils.vlog(f"{player_state.total_turns_spent + 1}: Using the banisher {self.name} on {utils.agreement(monster)} {monster.name}.")

    @staticmethod
    def get_banishers():
        return [Banisher(name="Spring Bumper", turn_duration=30, max_available_uses=999, has_cooldown=True, is_free=True),  # Add number of banishers in a variable
                Banisher(name="Throw Latte", turn_duration=30, max_available_uses=4, has_cooldown=True, is_free=True),
                Banisher(name="Reflex hammer", turn_duration=30, max_available_uses=3, has_cooldown=False, is_free=True),
                Banisher(name="KGB dart", turn_duration=20, max_available_uses=3, has_cooldown=False, is_free=True),
                Banisher(name="human musk", turn_duration=9999, max_available_uses=3, has_cooldown=False, is_free=True),
                Banisher(name="Batter Up!", turn_duration=9999, max_available_uses=999, has_cooldown=False, is_free=False)]
