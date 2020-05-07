import collections
import random
import math
import statistics

from Banisher import Banisher
from Copier import Copier
from Location import Location
from Encounter import Encounter
from Encounter import NonCombat
from Encounter import Combat


class Utils():

    def log(message):
        print(message)


class Simulator():

    def do_quest(self, player_state):
        park = Park()
        while park.progress < 1:
            park.resolve_turn(player_state, park)
        return player_state, park

    def run_simulator(self, iterations = 1000):
        turns = []
        banishers = []

        for a in range(iterations):
            player_state, park = self.do_quest(PlayerState())
            turns.append(player_state.get_total_turns_spent())
            banishers.append(park.get_banishers_used())

        Utils.log("In {} instances at {}% +NC it took an average of {} turns to complete the quest, with a median of {} and a deviation of {}."
        .format(iterations, PlayerState().player_nc, statistics.mean(turns), statistics.median(turns), statistics.pstdev(turns)))


class PlayerState():

    def __init__(self):
        self.player_nc = 25 # Change your current +non-combat% modifier here.
        self.player_item = 400 # Change your current +item% modifier here.
        self.total_turns_spent = 0
        self.wishes = 3
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
                            "half-size scalpel": 0,
                            "head mirror": 0,
                            "surgical apron": 0,
                            "surgical mask": 0
                            }

    def get_player_nc(self):
        return self.player_nc

    def nc_mod(self):
        return mod_cap(self.player_nc)

    def item_mod(self):
        return 1 + (self.player_item/100)

    def get_total_turns_spent(self):
        return self.total_turns_spent

    def incr_total_turns_spent(self):
        self.total_turns_spent += 1

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

    def get_inventory_item(self, item):
        return self.inventory[item]

    def incr_inventory_item(self, item):
        self.inventory[item] += 1

    def decr_inventory_item(self, item):
        self.inventory[item] -= 1

    def check_copier(self, location, encounter):
        for copier in self.copiers:
            if (copier.get_copied_mob(self) != encounter.get_name()) and copier.check(self):
                copier.use(location, self, encounter)
        return True

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

    def mod_cap(virgin_mod):
        if virgin_mod < 0:
            return 0
        if virgin_mod > 25:
            return 20 + math.floor(virgin_mod/5)
        return virgin_mod


class Park(Location):

    class Dakota(Encounter):

        def check(self, location, player_state):
            return (location.get_delay() - location.get_turns_spent()) < 1

        def run(self, location, player_state):
            player_state.incr_inventory_item("antique machete")
            location.incr_progress()
            super().run(location, player_state)


    class Dumpster(Encounter): # Doesn't need queue logic

        def run(self, location, player_state):
            if not player_state.get_janitors_moved():
                player_state.set_janitors_moved()
            else:
                player_state.incr_inventory_item(location.roll_dumpster_item())
                if random.randrange(20) == 1:
                    player_state.incr_inventory_item("short writ of habeas corpus")
            super().run(location, player_state)


    class Janitor(Combat):

        def check(self, location, player_state):
            return player_state.get_janitors_moved()


    def __init__(self):
        super().__init__(
            15, #Native Non-Combat rate of location
            [   #Superlikelies go here
                Park.Dakota("Dr. Henry \"Dakota\" Fanning, Ph.D., R.I.P.")
            ],
            [   #NCs go here
                Park.Dumpster("Where Does The Lone Ranger Take His Garbagester?")
            ],
            [   #"Combat Name", "Phylum", should_banish, should_sniff, item_drops
                Combat("Boaraffe", "Beast", True, False),
                Combat("Pygmy Assault Squad", "Dude", False),
                Combat("Pgymy Blowgunner", "Dude", True, False),
                Park.Janitor("Pygmy Janitor", "Dude", True, False, {"book of matches": 20})
            ],
            6, # Turns of delay
            0, # Number of banishers to commit to the location
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


if __name__ == "__main__":
    Simulator().run_simulator()
