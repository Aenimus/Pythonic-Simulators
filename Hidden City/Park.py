import random

from Location import Location
from Encounter import Encounter
from Encounter import Turn
from Encounter import BaseCombat
from Encounter import Combat

banishers = 0 # The number of banishers you wish to commit to the location
macros = 0 # The number of macros you wish to commit to the location

class Park(Location):

    class Dakota(Turn):

        def check(self, location, player_state):
            return (location.get_delay() - location.get_turns_spent()) < 1

        def run(self, location, player_state):
            super().run(location, player_state)
            player_state.incr_inventory_item("antique machete")
            location.incr_progress()


    class Dumpster(Turn): # Doesn't need queue logic

        def run(self, location, player_state):
            super().run(location, player_state)
            if not player_state.get_janitors_moved():
                player_state.set_janitors_moved()
            else:
                player_state.incr_inventory_item(location.roll_dumpster_item())
                if random.randrange(20) == 1:
                    player_state.incr_inventory_item("short writ of habeas corpus")


    class Janitor(Combat):

        def check(self, location, player_state):
            return player_state.get_janitors_moved()


    def __init__(self):
        super().__init__(
            "The Hidden Park",
            15, #Native Non-Combat rate of location
            [   #Superlikelies go here
                Park.Dakota("Dr. Henry \"Dakota\" Fanning, Ph.D., R.I.P.")
            ],
            [   #NCs go here
                Park.Dumpster("Where Does The Lone Ranger Take His Garbagester?")
            ],
            [   #"Combat Name", "Phylum", should_banish, should_sniff, should_macro, item_drops
                Combat("Boaraffe", "Beast", False, False, False),
                Combat("Pygmy Assault Squad", "Dude", False, False, False),
                Combat("Pgymy Blowgunner", "Dude", True, False, False),
                Park.Janitor("Pygmy Janitor", "Dude", False, False, False, {"book of matches": 20})
            ],
            6, # Turns of delay
            banishers, # Number of banishers to commit to the location
            macros # Number of macros to commit to the location
        )
        self.dumpster_items = [
                                "bloodied surgical dungarees",
                                "bowling ball",
                                "half-size scalpel",
                                "head mirror",
                                "surgical apron",
                                "surgical mask"
        ]

    def get_dumpster_items(self):
        return self.dumpster_items

    def roll_dumpster_item(self): # Assumes you closet bowling balls immediately
        items = self.get_dumpster_items()
        return items[random.randrange(len(items))]
