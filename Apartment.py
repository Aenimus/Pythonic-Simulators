from Location import Location
from Encounter import Encounter
from Encounter import Turn
from Encounter import BaseCombat
from Encounter import Combat

banishers = 1 # The number of banishers you wish to commit to the location
macros = 3 # The number of macros you wish to commit to the location

class Apartment(Location):

    class Elevator(Turn):

        def check(self, location, player_state):
            return location.get_pity_timer() > 8

        def run(self, location, player_state):
            super().run(location, player_state)
            if player_state.get_cursed_level() > 2:
                location.incr_progress()
            else:
                player_state.incr_cursed_level()
            location.set_pity_timer(1)

    class Accountant(Combat):

        def run(self, location, player_state):
            super().run(location, player_state)
            player_state.incr_accountants_fought()


    class Janitor(Combat):

        def check(self, location, player_state):
            return not player_state.get_janitors_moved()


    class Shaman(BaseCombat):

        def run(self, location, player_state):
            super().run(location, player_state)
            if location.get_add_queue(): # Handled like this for saber later
                self.add_com_queue(location)
                player_state.incr_cursed_level()
            if location.get_macrod():
                location.reset_macrod()
                location.reset_add_queue()
            elif location.should_macro(player_state, self):
                return location.resolve_macro(player_state, self)
            if self.should_banish:
                player_state.check_banisher(location, self)
            elif self.should_copy:
                player_state.check_copier(location, self)
            location.incr_pity_timer()
            if location.get_free_turn():
                location.set_free_turn(True)
                return True
            location.incr_turns_spent()
            player_state.incr_total_turns_spent()


    def __init__(self):
        super().__init__(
            "The Hidden Apartment",
            0, #Native Non-Combat rate of location
            [   #Superlikelies go here
                Apartment.Elevator("Action Elevator")
            ],
            [   #NCs go here
            ],
            [   #"Combat Name", "phylum", should_banish, should_sniff, should_macro, item_drops
                Apartment.Shaman("Pygmy Shaman", "Dude", False, False, True),
                Apartment.Janitor("Pygmy Janitor", "Dude", True, False, False),
                Apartment.Accountant("Pygmy Witch Accountant", "Dude", False, False, False),
                Combat("Pgymy Witch Lawyer", "Dude", True, False, False, {"short writ of habeas corpus": 5})
            ],
            0, # Turns of delay
            banishers, # Number of banishers to commit to the location
            macros # Number of macros to commit to the location
        )
