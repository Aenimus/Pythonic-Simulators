from Location import Location
from Encounter import Encounter
from Encounter import Turn
from Encounter import BaseCombat
from Encounter import Combat

banishers = 1 # The number of banishers you wish to commit to the location
macros = 0 # The number of macros you wish to commit to the location

class Office(Location):

    class Holiday(Turn):

        def check(self, location, player_state):
            return location.get_pity_timer() > 5

        def run(self, location, player_state):
            super().run(location, player_state)
            if location.get_progress() < 1:
                location.incr_progress()
            elif player_state.get_accountants_fought() > 4:
                location.incr_progress()
            location.set_pity_timer(1)


    class Accountant(Combat):

        def run(self, location, player_state):
            super().run(location, player_state)
            player_state.incr_accountants_fought()


    class Janitor(Combat):

        def check(self, location, player_state):
            return not player_state.get_janitors_moved()


    def __init__(self):
        super().__init__(
            "The Hidden Office",
            0, #Native Non-Combat rate of location
            [   #Superlikelies go here
                Office.Holiday("Working Holiday")
            ],
            [   #NCs go here
            ],
            [   #"Combat Name", "phylum", should_banish, should_sniff, should_macro, item_drops {}
                Combat("Pygmy Headhunter", "Dude", False, False, False),
                Office.Janitor("Pygmy Janitor", "Dude", True, False, False),
                Office.Accountant("Pygmy Witch Accountant", "Dude", False, False, False),
                Combat("Pgymy Witch Lawyer", "Dude", True, False, False, {"short writ of habeas corpus": 5})
            ],
            0, # Turns of delay
            banishers, # Number of banishers to commit to the location
            macros # Number of macros to commit to the location
        )
