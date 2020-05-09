from Location import Location
from Encounter import Encounter
from Encounter import Turn
from Encounter import BaseCombat
from Encounter import Combat

banishers = 3 # The number of banishers you wish to commit to the location
macros = 0 # The number of macros you wish to commit to the location

class Alley(Location):

    class Bowls(Turn):

        def check(self, location, player_state):
            return player_state.get_inventory_item("bowling ball") > 0

        def run(self, location, player_state):
            super().run(location, player_state)
            location.incr_progress()
            if location.get_progress() < 5:
                player_state.decr_inventory_item("bowling ball")


    class Drunk(BaseCombat):

        def check(self, location, player_state):
            return not player_state.get_janitors_moved()

        def run(self, location, player_state):
            super().run(location, player_state)
            if location.get_add_queue() and player_state.get_inventory_item("book of matches") > 0:
                self.add_com_queue(location)
                return True
            if location.get_macrod(): # If we macrod the previous combat
                location.set_macrod(False)
                location.set_add_queue(True)
            elif location.should_macro(player_state, self):
                return location.resolve_macro(player_state, self)
            if self.should_banish: # Banish and copy are mutually exclusive
                player_state.check_banisher(location, self)
            elif self.should_copy:
                player_state.check_copier(location, self)
            if location.get_free_turn():
                if verbose:
                    print("Turn {} was a free turn.".format(player_state.get_total_turns_spent()))
                location.set_free_turn(False)
                return True
            location.incr_turns_spent()
            player_state.incr_total_turns_spent()


    class Janitor(Combat):

        def check(self, location, player_state):
            return not player_state.get_janitors_moved()


    def __init__(self):
        super().__init__(
            "The Hidden Bowling Alley",
            0, #Native Non-Combat rate of location
            [   #Superlikelies go here
                Alley.Bowls("Life is Like a Cherry of Bowls")
            ],
            [   #NCs go here
            ],
            [   #"Combat Name", "Phylum", should_banish, should_sniff, should_macro item_drops
                Alley.Drunk("Drunk Pgymy", "Dude", True, False, False),
                Combat("Pygmy Bowler", "Dude", False, True, False, {"bowling ball": 40}),
                Alley.Janitor("Pygmy Janitor", "Dude", True, False, False),
                Combat("Pygmy Orderlies", "Dude", True, False, False),
            ],
            0, # Turns of delay
            banishers, # Number of banishers to commit to the location
            macros # Number of macros to commit to the location
        )
