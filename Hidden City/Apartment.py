from Location import Location
from Encounter import Phylum, Superlikely, Combat
from Office import accountant, janitor, lawyer


# The Hidden apartment
def elevator_check(encounter, player_state, location, **kwargs):
    turns_spent = player_state.locations[location].turns_spent
    return (turns_spent % encounter.delay) == 0 and turns_spent > 0

def elevator_run(encounter, player_state, location, **kwargs):
    if player_state.cursed_level > 2:
        player_state.locations[location].increment_progress(player_state, location)
    else:
        player_state.cursed_level += 1

elevator = Superlikely(name="Elevator", delay=8, validator=elevator_check, run4=elevator_run)

# Pygmy Accountant
def shaman_run(encounter, player_state, location, **kwargs):
    if player_state.cursed_level < 3:
        player_state.cursed_level += 1

shaman = Combat(name="Pygmy Shaman", phylum=Phylum.DUDE, run1=shaman_run)

apartment = Location(name="The Hidden Apartment", encounters=[elevator, accountant, janitor, lawyer, shaman])


