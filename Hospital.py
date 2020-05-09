import random

from Location import Location
from Encounter import Encounter
from Encounter import Turn
from Encounter import BaseCombat
from Encounter import Combat

banishers = 1
macros = 0

class Hospital(Location):

    class Md(Turn):

        def check(self, location, player_state):
            surgeonosity = player_state.get_surgeonosity() * 1
            return random.randrange(10) < surgeonosity


        def run(self, location, player_state):
            super().run(location, player_state)
            location.incr_progress()


    class Janitor(Combat):

        def check(self, location, player_state):
            return not player_state.get_janitors_moved()


    class Surgeon(Combat):

        def run(self, location, player_state):
            if player_state.get_surgeonosity() < 5:
                player_state.incr_surgeonosity()
            super().run(location, player_state)


    def __init__(self, player_state):
        super().__init__(
            "The Hidden Hospital",
            0, #Native Non-Combat rate of location
            [   #Superlikelies go here
                Hospital.Md("You, M. D.")
            ],
            [   #NCs go here
            ],
            [   #"Combat Name", "phylum", should_banish, should_sniff, should_macro, item_drops {}
                Hospital.Janitor("Pygmy Janitor", "Dude", True, False, False),
                Combat("Pygmy Orderlies", "Dude", True, False, False),
                Hospital.Surgeon("Pygmy Witch Surgeon", "Dude", False, True, False),
                Combat("Pygmy Witch Nurse", "Dude", True, False, False)
            ],
            0, # Turns of delay
            banishers, # Number of banishers to commit to the location
            macros # Number of macros to commit to the location
        )
        self.surgeon_gear = [
                                "bloodied surgical dungarees",
                                "half-size scalpel",
                                "head mirror",
                                "surgical apron",
                                "surgical mask"
                            ]

        for gear in self.surgeon_gear:
            if player_state.get_inventory_item(gear) > 0:
                player_state.incr_surgeonosity()
