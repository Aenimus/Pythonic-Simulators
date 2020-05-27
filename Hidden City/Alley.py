from Location import Location
from Encounter import Phylum, Superlikely, Combat

import utils
from Items import Items
from Hospital import janitor, orderlies


# Life is Like a Cherry of Bowls
def bowls_check(encounter, player_state, location, **kwargs):
    return player_state.inventory[Items.BowlingBall]

def bowls_run(encounter, player_state, location, **kwargs):
    player_state.locations[location].increment_progress(player_state, location)
    if player_state.locations[location].progress < 5:
        player_state.inventory[Items.BowlingBall] -= 1

bowls = Superlikely(name="Life is Like a Cherry of Bowls", validator=bowls_check, run4=bowls_run)

# Drunk Pygmy
def drunk_run(encounter, player_state, location, **kwargs):
    if player_state.inventory[Items.BookOfMatches]:
        player_state.free_turn = True
        player_state.should_roll_drops = False
        utils.vlog("Used a bowl of scoprions to complete the combat without using a turn.")

bowler = Combat(name="Pygmy Bowler", phylum=Phylum.DUDE, item_drops={Items.BowlingBall: 40})

drunk = Combat(name="Drunk Pygmy", phylum=Phylum.DUDE, run1=drunk_run)

orderlies = Combat(name="Pygmy Orderlies", phylum=Phylum.DUDE, group=True)

witch = Combat(name="Pygmy Witch", phylum=Phylum.DUDE)

alley = Location(name="The Hidden Bowling Alley", encounters=[bowls, bowler, drunk, janitor, orderlies])



