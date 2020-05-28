import random

from Location import Location
from Encounter import Phylum, Superlikely, Combat

from Items import SURGEON_GEAR
from Office import janitor


# The Hidden Hospital
def md_check(encounter, player_state, location, **kwargs):
    return random.randrange(10) < player_state.surgeonosity

def md_run(encounter, player_state, location, **kwargs):
    player_state.locations[location].increment_progress(player_state, location)

md = Superlikely(name="You, M. D.", validator=md_check, run4=md_run)

# Pygmy Surgeon
def surgeon_run(encounter, player_state, location, **kwargs):
    for gear in SURGEON_GEAR:
        if player_state.inventory[gear] < 1:
            player_state.inventory[gear] += 1
            break

surgeon = Combat(name="Pygmy Surgeon", phylum=Phylum.DUDE, run4=surgeon_run)

orderlies = Combat(name="Pygmy Orderlies", phylum=Phylum.DUDE, group=True)

nurse = Combat(name="Pygmy Witch Nurse", phylum=Phylum.DUDE)

hospital = Location(name="The Hidden Hospital", encounters=[md, janitor, nurse, orderlies, surgeon])


