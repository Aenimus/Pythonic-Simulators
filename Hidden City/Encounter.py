import random
import math

verbose = True

class Encounter():

    def __init__(self, name = "", delay = 0):
        self.name = name
        self.delay = delay

    def __str__(self):
        return "Encounter({})".format(self.name)

    def get_name(self):
        return self.name

    def check(self, location, player_state):
        return True

    def run(self, location, player_state):
        if verbose:
            name = self.name
            print("{}: Encountered {} at {} location progress.".format(player_state.get_total_turns_spent() + 1, name, location.get_progress()))


class Turn(Encounter):

    def run(self,location, player_state):
        super().run(location, player_state)
        location.incr_turns_spent()
        player_state.incr_total_turns_spent()


class NonCombat(Encounter):

    def add_nc_queue(self, location, nc = None):
        if nc is None:
            nc = self.name
        location.append_nc_history(nc)

    def run(self, location, player_state):
        super().run(location, player_state)
        self.add_nc_queue(location)
        location.incr_turns_spent()
        player_state.incr_total_turns_spent()


class BaseCombat(Encounter):

    def __init__(self, name = "", phylum = None, banish = False, copy = False, should_macro = False, item_drops = {}):
        super().__init__(name)
        self.phylum = phylum
        self.wish = False
        self.should_banish = banish
        self.should_copy = copy
        self.should_macro = should_macro
        self.should_roll_drops = True
        self.item_drops = item_drops

    def get_phylum(self):
        return self.phylum

    def get_use_all_sniffs(self):
        return self.use_all_sniffs

    def set_should_roll_drops(self, boolean):
        self.should_roll_drops = boolean

    def get_should_macro(self):
        return self.should_macro

    def check(self, location, player_state):
        for banisher in player_state.get_banishers():
            if banisher.get_banished_mob(player_state) == self.name:
                return False
        return True

    def add_com_queue(self, location, combat = None):
        if combat is None:
            combat = self.name
        location.append_combat_history(combat)

    def roll_drops(self, player_state):
        if len(self.item_drops):
            for item in self.item_drops:
                if random.randrange(100) < (math.floor(self.item_drops.get(item) * player_state.get_item_mod())):
                    player_state.incr_inventory_item(item)


class Combat(BaseCombat):



    def run(self, location, player_state):
        super().run(location, player_state)
        if location.get_add_queue(): # Handled like this for saber later
            self.add_com_queue(location)
        if location.get_macrod(): # If we macrod the previous combat
            location.set_macrod(False)
            location.set_add_queue(True)
        elif location.should_macro(player_state, self):
            return location.resolve_macro(player_state, self)
        if self.should_banish: # Banish and copy are mutually exclusive
            player_state.check_banisher(location, self)
        elif self.should_copy:
            player_state.check_copier(location, self)
        if self.should_roll_drops: # Default is to roll drops; if False, resets back to True.
            self.roll_drops(player_state)
        else:
            self.should_roll_drops = True
        location.incr_pity_timer()
        if location.get_free_turn():
            if verbose:
                print("Turn {} was a free turn.".format(player_state.get_total_turns_spent() + 1))
            location.set_free_turn(False)
            return True
        location.incr_turns_spent()
        player_state.incr_total_turns_spent()
