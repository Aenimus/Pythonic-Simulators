import math

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
        if location.get_free_turn():
            location.toggle_free_turn()
            return True
        location.incr_turns_spent()
        player_state.incr_total_turns_spent()


class NonCombat(Encounter):

    def add_nc_queue(self, location, nc = None):
        if nc is None:
            nc = self.name
        location.append_nc_history(nc)

    def run(self, location, player_state):
        self.add_com_queue(location)
        super().run(location, player_state)


class Combat(Encounter):

    def __init__(self, name = "", delay = 0, phylum = None, banish = False, copy = False, should_macro = False, item_drops = {}):
        super().__init__(self, name)
        self.phylum = phylum
        self.wish = False
        self.should_banish = banish
        self.should_copy = copy
        self.should_macro = should_macro
        self.item_drops = item_drops

    def get_phylum(self):
        return self.phylum

    def get_use_all_sniffs(self):
        return self.use_all_sniffs

    def check(self, location, player_state):
        for banisher in player_state.get_banishers():
            if banisher.get_banished_mob(player_state) == self.name:
                return False
        return True

    def add_com_queue(self, location, combat = None):
        if combat is None:
            combat = self.name
        location.append_combat_history(combat)

    def check_drops(self, location, player_state):
        if len(self.item_drops):
            for item in self.item_drops:
                if random.randrange(100) < (math.floor(self.item_drops.get(item) * player_state.item_mod())):
                    player_state.incr_inventory_item(item)

    def run(self, location, player_state):
        if location.get_add_queue(): # Handled like this for saber later
            self.add_com_queue(location)
        if location.get_macrod():
            location.reset_macrod()
            location.reset_add_queue()
        elif self.should_macro:
            return location.select_macro_combat(player_state, self)
        if self.should_banish:
            player_state.check_banisher(location, self)
        elif self.should_copy:
            player_state.check_copier(location, self)
        super().run(location, player_state)
