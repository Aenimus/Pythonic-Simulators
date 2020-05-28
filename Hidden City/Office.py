import utils
from Location import Location
from Encounter import Phylum, Superlikely, Combat
from Items import Items


# The Hidden Office
def holiday_check(encounter, player_state, location, **kwargs):
    turns_spent = player_state.locations[location].turns_spent
    return (turns_spent % encounter.delay) == 0 and turns_spent > 0

def holiday_run(encounter, player_state, location, **kwargs):
    if player_state.inventory[Items.BoringBinderClip] < 1:
        player_state.inventory[Items.BoringBinderClip] +=1
        utils.vlog(f"{player_state.total_turns_spent + 1}: Gained a boring binder clip.")
    elif player_state.accountants_fought > 4:
        player_state.locations[location].increment_progress(player_state, location)

holiday = Superlikely(name="Working Holiday", delay=5, validator=holiday_check, run4=holiday_run)

# Pygmy Accountant
def accountant_run(encounter, player_state, location, **kwargs):
    player_state.accountants_fought += 1

accountant = Combat(name="Pygmy Accountant", phylum=Phylum.DUDE, run4=accountant_run)

headhunter = Combat(name="Pygmy Headhunter", phylum=Phylum.DUDE)

def janitor_check(encounter, player_state, location, **kwargs):
   # print(f"janitors_moved is {player_state.janitors_moved}")
    return not player_state.janitors_moved

janitor = Combat(name="Pygmy Janitor", phylum=Phylum.DUDE, validator=janitor_check, item_drops={Items.BookOfMatches: 20})

lawyer = Combat(name="Pygmy Witch Lawyer", phylum=Phylum.DUDE, item_drops={Items.ShortWritOfHabeasCorpus: 5})

office = Location(name="The Hidden Office", encounters=[holiday, accountant, janitor, lawyer, headhunter])
