import statistics
import random

from collections import defaultdict

import utils
from Items import Items
from Location import Location
from PlayerState import PlayerState, Decisions
from Encounter import Phylum, Combat
from Hospital import nurse, orderlies, md
from Items import Items, SURGEON_GEAR

threshold = 5

# Pygmy Surgeon
def surgeon_run(encounter, player_state, location, **kwargs):
    if player_state.surgeonosity < threshold:
        for gear in SURGEON_GEAR:
            if player_state.inventory[gear] < 1:
                player_state.inventory[gear] += 1
                break
    else:
        utils.vlog(f"Ran away from a surgeon at {player_state.surgeonosity} surgeonosity.")

surgeon = Combat(name="Pygmy Surgeon", phylum=Phylum.DUDE, run4=surgeon_run)

hospital = Location(name="The Hidden Hospital", encounters=[md, nurse, orderlies, surgeon])


utils.verbose = False
iterations = 1000 # Change the number of simulations here.
total_available_macros = 10 # Change your total available number of macros here.
my_non_combat_rate = 25 # Change the +non-combat% modifier here.
my_item_drops = 400  # Change the +item% modifier here.


decisions = Decisions(banishers_per_location = {hospital: 2},
                      banisher_targets = [nurse, orderlies],
                      copier_targets = [surgeon])

class Simulator():
    def do_quest(self, player_state: PlayerState):
        while player_state.locations[hospital].progress < 1:
            hospital.resolve_turn(player_state)

    def run_simulator(self, iterations: int):
        turns = []
        loc_turns = defaultdict(list)
        total_banishers = 0
        total_macros = 0

        for _ in range(iterations):
            player_state = PlayerState(decisions=decisions, nc_mod=my_non_combat_rate, item_mod=my_item_drops, available_macros=total_available_macros)
            player_state.inventory[Items.BloodiedSurgicalDungarees] += 1
            player_state.inventory[Items.SurgicalApron] += 1
            #player_state.inventory[Items.HalfSizeScalpel] += 1
            #player_state.inventory[Items.SurgicalMask] += 1
            #player_state.inventory[Items.HeadMirror] += 1
            self.do_quest(player_state)
            turns.append(player_state.total_turns_spent)
            for loc in player_state.locations:
                banishers_used = player_state.locations[loc].banishers_used
                macros_used = player_state.locations[loc].macros_used
                total_banishers += banishers_used
                total_macros += macros_used
                loc_turns[loc].append(player_state.locations[loc].turns_spent)

        utils.log(f"In {iterations} instances at {threshold} max surgeonosity, and an average of {total_banishers / iterations} banishers and {total_macros / iterations} macros, it took an average of {statistics.mean(turns)} turns to complete the Hidden Hopsital, with a median of {statistics.median(turns)} and a deviation of {statistics.pstdev(turns)}.")

        for key in loc_turns:
            mean = statistics.mean(loc_turns[key])
            plural = "s" if mean > 1 else ""
            utils.log(f"{key}: {mean} turn{plural}")

if __name__ == "__main__":
    Simulator().run_simulator(iterations)
