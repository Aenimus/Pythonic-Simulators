import math
import statistics

from Banisher import Banisher
from Copier import Copier

from Park import Park
from Office import Office
from Apartment import Apartment
from Alley import Alley
from Hospital import Hospital

iterations = 1 # Change the number of simulations here.
starting_macros = 10 # Change your starting number of macros here.
my_non_combat_rate = 25 # Change the +non-combat% modifier here.
my_item_drops = 400  # Change the +item% modifier here.


class Utils():

    def log(message):
        print(message)

    def dictionary_append(dictionary, key, value):
        if key not in dictionary:
            dictionary[key] = [value]
        else:
            dictionary[key].append(value)


class Simulator():

    def do_quest(self, player_state):
        park = Park()
        while player_state.get_inventory_item("antique machete") < 1:
            park.resolve_turn(player_state)
        apartment = Apartment()
        while apartment.get_progress() < 1:
            apartment.resolve_turn(player_state)
        office = Office()
        while office.get_progress() < 2:
            office.resolve_turn(player_state)
        alley = Alley()
        while alley.get_progress() < 5:
            alley.resolve_turn(player_state)
        hospital = Hospital(player_state)
        while hospital.get_progress() < 1:
            hospital.resolve_turn(player_state)
        player_state.incr_total_turns_spent(5) # Unlock 4 locations and fight the boss
        return player_state, park, office, apartment, alley, hospital

    def run_simulator(self, iterations):
        turns = []
        loc_turns = {}
        total_banishers = 0
        total_macros = 0
        banishers = []
        macros = []

        for a in range(iterations):
            player_state, park, office, apartment, alley, hospital = self.do_quest(PlayerState())
            locs = [park, office, apartment, alley, hospital]
            turns.append(player_state.get_total_turns_spent())
            for loc in locs:
                banishers_used = loc.get_banishers_used()
                macros_used = loc.get_macros_used()
                total_banishers += banishers_used
                total_macros += macros_used
                banishers.append(banishers_used)
                macros.append(loc.get_macros_used())
                Utils.dictionary_append(loc_turns, loc, loc.get_turns_spent())

        Utils.log("In {} instances at {}% +NC and an average of {} banishers and {} macros, it took an average of {} turns to complete the Hidden City quest, with a median of {} and a deviation of {}."
        .format(iterations, player_state.player_nc, total_banishers / iterations, total_macros / iterations, statistics.mean(turns), statistics.median(turns), statistics.pstdev(turns)))

        for key in loc_turns:
            mean = statistics.mean(loc_turns[key])
            plural = "s" if mean > 1 else ""
            Utils.log("{}: {} turn{}".format(key, mean, plural))
        Utils.log("And 5 turns for unlocks and the boss.".)


class PlayerState():

    def __init__(self):
        self.player_nc = my_non_combat_rate # Change your current +non-combat% modifier here.
        self.player_item = my_item_drops # Change your current +item% modifier here.
        self.total_turns_spent = 0
        self.wishes = 3
        self.macros = starting_macros
        self.banishers = [ #"Banisher Name", duration, max_available_uses, has_cooldown, is_free
                            Banisher("Spring Bumper", 30, 999, True, True), #Add number of banishers in a variable
                            Banisher("Throw Latte", 30, 4, True, True),
                            Banisher("Reflex hammer", 30, 3, False, True),
                            Banisher("KGB dart", 20, 3, False, True),
                            Banisher("Batter Up!", 9999, 999, False, False)
                        ]
        self.copiers = [ #"Copy Name", duration, max_available_uses, has_cooldown, number_of_copies, ignores_rejection
                            Copier("Olfaction", 40, 999, True, 3, False),
                            Copier("Share Latte", 30, 3, True, 2),
                            Copier("Mating Call", 999, 1, False, 1)
                        ]
        self.tracked_phylum = ""
        self.olfacted_mob = None
        self.latted_mob = None
        self.mated_mob = None
        self.janitors_moved = False
        self.accountants_fought = 0
        self.cursed_level = 0
        self.surgeonosity = 0

        self.inventory = {
                            "ketchup hound": 0,
                            "another item": 0,
                            "disposable instant camera": 1,
                            "photograph of a dog": 0,
                            "I Love Me, Vol. I": 0,
                            "photograph of a red nugget": 0,
                            "photograph of an ostrich egg": 0,
                            "photograph of God": 0,
                            "antique machete": 0,
                            "short writ of habeas corpus": 0,
                            "bloodied surgical dungarees": 0,
                            "bowling ball": 0,
                            "book of matches": 0,
                            "half-size scalpel": 0,
                            "head mirror": 0,
                            "surgical apron": 0,
                            "surgical mask": 0
                        }

    def get_player_nc(self):
        return self.player_nc

    def nc_mod(self):
        return mod_cap(self.player_nc)

    def get_item_mod(self):
        return 1 + (self.player_item / 100)

    def get_total_turns_spent(self):
        return self.total_turns_spent

    def incr_total_turns_spent(self, num=1):
        self.total_turns_spent += num

    def get_wishes(self):
        return self.wishes

    def get_banishers(self):
        return self.banishers

    def get_olfacted_mob(self):
        return self.olfacted_mob

    def set_olfacted_mob(self, encounter_name):
        self.olfacted_mob = encounter_name

    def reset_olfacted_mob(self):
        self.olfacted_mob = None

    def get_extra_copies(self, encounter):
        if encounter.get_phylum() == self.tracked_phylum:
            extra_copies = 2
        else:
            extra_copies = 0
        name = encounter.get_name()
        for copier in self.copiers:
            if copier.get_copied_mob(self) == name:
                extra_copies += copier.get_copies()
        return extra_copies

    def get_janitors_moved(self):
        return self.janitors_moved

    def set_janitors_moved(self):
        self.janitors_moved = True

    def get_accountants_fought(self):
        return self.accountants_fought

    def incr_accountants_fought(self):
        self.accountants_fought += 1

    def get_cursed_level(self):
        return self.cursed_level

    def incr_cursed_level(self):
        self.cursed_level += 1

    def get_surgeonosity(self):
        return self.surgeonosity

    def incr_surgeonosity(self):
        self.surgeonosity += 1

    def get_inventory_item(self, item):
        return self.inventory[item]

    def incr_inventory_item(self, item, num = 1):
        self.inventory[item] += num

    def decr_inventory_item(self, item, num = 1):
        self.inventory[item] -= num

    def get_macros(self):
        return self.macros

    def decr_macros(self, num = 1):
        self.macros -= num

    def choose_banisher(self, encounter):
        avail_banisher = None
        for banisher in self.banishers:
            if banisher.get_banished_mob(self) == encounter.get_name():
                return False
            if (not avail_banisher) and banisher.check(self):
                avail_banisher = banisher
                return avail_banisher
        return avail_banisher

    def check_banisher(self, location, encounter):
        if location.get_banishers_left():
            banisher = self.choose_banisher(encounter)
            if banisher:
                banisher.use(location, self, encounter)
                return True
        return False

    def check_copier(self, location, encounter):
        for copier in self.copiers:
            if (copier.get_copied_mob(self) != encounter.get_name()) and copier.check(self):
                copier.use(location, self, encounter)
        return True

    def mod_cap(virgin_mod):
        if virgin_mod < 0:
            return 0
        if virgin_mod > 25:
            return 20 + math.floor(virgin_mod/5)
        return virgin_mod

if __name__ == "__main__":
    Simulator().run_simulator(iterations)
