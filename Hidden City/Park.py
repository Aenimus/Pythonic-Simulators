import random

import utils
from Items import Items, DUMPSTER_ITEMS
from Location import Location
from Encounter import Phylum, Superlikely, NonCombat, Combat

boaraffe = Combat(name="Boaraffe", phylum=Phylum.BEAST)

squad = Combat(name="Pygmy Assault Squad", phylum=Phylum.DUDE)

blowgunner = Combat(name="Pgymy Blowgunner", phylum=Phylum.DUDE)

# Pygmy Janitor
def janitor_check(encounter, player_state, location, **kwargs):
    return player_state.janitors_moved

janitor = Combat(name="Pygmy Janitor", phylum=Phylum.DUDE, validator=janitor_check, item_drops={Items.BookOfMatches: 20})

# Dakota
def dakota_check(encounter, player_state, location, **kwargs):
    turns_spent = player_state.locations[location].turns_spent
    return turns_spent >= encounter.delay

def dakota_run(encounter, player_state, location, **kwargs):
    player_state.inventory[Items.AntiqueMachete] += 1

dakota = Superlikely(name="Dr. Henry \"Dakota\" Fanning, Ph.D., R.I.P.", delay=6, validator=dakota_check, run4=dakota_run)

# Dumpster; assumes you closet bowling balls immediately
def roll_dumpster_item():
    return random.choice(DUMPSTER_ITEMS)

def dumpster_run(encounter, player_state, location, **kwargs):
    if not player_state.janitors_moved:
        player_state.janitors_moved = True
        utils.vlog(f"{player_state.total_turns_spent}: Pygmy janitors moved to the park.")
    else:
        item = roll_dumpster_item()
        player_state.inventory[item] += 1
        utils.vlog(f"Acquired 1 {Items.get_name(item)} from the dumpster.")
        if not random.randrange(20):
            player_state.inventory[Items.ShortWritOfHabeasCorpus] += 1
            utils.vlog(f"Acquired 1 {Items.get_name(Items.ShortWritOfHabeasCorpus)} from the dumpster.")

dumpster = NonCombat(name="Where Does The Lone Ranger Take His Garbagester?", run4=dumpster_run)

park = Location(name="The Hidden Hospital", nc=15, encounters=[dakota, dumpster, boaraffe, blowgunner, janitor, squad])


