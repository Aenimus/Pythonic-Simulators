import statistics
from collections import defaultdict

import utils
from Items import Items
from PlayerState import PlayerState, Decisions
from Park import park
from Office import office, headhunter, lawyer
from Apartment import apartment, shaman
from Alley import alley, bowler, orderlies
from Hospital import hospital, surgeon

utils.verbose = True
iterations = 1 # Change the number of simulations here.
total_available_macros = 10 # Change your total available number of macros here.
my_non_combat_rate = 25 # Change the +non-combat% modifier here.
my_item_drops = 400  # Change the +item% modifier here.


decisions = Decisions(banishers_per_location = {office: 2, apartment: 1, alley: 1, hospital: 2},
                      macros_per_location = {office: 0, apartment: 3, alley: 0, hospital: 0},
                      banisher_targets = [lawyer, orderlies, headhunter],
                      macro_targets = [shaman],
                      copier_targets = [bowler, surgeon])

class Simulator():
    def do_quest(self, player_state: PlayerState):
        while player_state.inventory[Items.AntiqueMachete] < 1:
            park.resolve_turn(player_state)
        utils.unlock(player_state)
        while player_state.locations[apartment].progress < 1:
            apartment.resolve_turn(player_state)
        utils.unlock(player_state)
        while player_state.locations[office].progress < 1:
            office.resolve_turn(player_state)
        utils.unlock(player_state)
        while player_state.locations[hospital].progress < 1:
            hospital.resolve_turn(player_state)
        utils.unlock(player_state)
        while player_state.locations[alley].progress < 5:
            alley.resolve_turn(player_state)
        utils.unlock(player_state)

    def run_simulator(self, iterations: int):
        turns = []
        loc_turns = defaultdict(list)
        total_banishers = 0
        total_macros = 0

        for _ in range(iterations):
            player_state = PlayerState(decisions=decisions, nc_mod=my_non_combat_rate, item_mod=my_item_drops, available_macros=total_available_macros)
            self.do_quest(player_state)
            turns.append(player_state.total_turns_spent)
            for loc in player_state.locations:
                banishers_used = player_state.locations[loc].banishers_used
                macros_used = player_state.locations[loc].macros_used
                total_banishers += banishers_used
                total_macros += macros_used
                loc_turns[loc].append(player_state.locations[loc].turns_spent)

        utils.log(f"In {iterations} instances at {my_non_combat_rate}% +NC and an average of {total_banishers / iterations} banishers and {total_macros / iterations} macros, it took an average of {statistics.mean(turns)} turns to complete the Hidden City quest, with a median of {statistics.median(turns)} and a deviation of {statistics.pstdev(turns)}.")

        for key in loc_turns:
            mean = statistics.mean(loc_turns[key])
            plural = "s" if mean > 1 else ""
            utils.log(f"{key}: {mean} turn{plural}")

        utils.log("And 5 turns for location unlocks and defeating the boss.")

if __name__ == "__main__":
    Simulator().run_simulator(iterations)
