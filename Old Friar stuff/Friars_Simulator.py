import collections
import random
import math
import statistics

class Utils():

    def log(message):
        print(message)


class Simulator():

    def do_quest(self, player_state):
        heart = FriarLoc()
        neck = FriarLoc()
        elbow = FriarLoc()
        while heart.progress < 4: #1 progress for each NC/superlikely, 1 for encountering 5 Dudes and 1 progress for either 8 dudes total or 1 Bob.
            heart.resolve_turn(player_state)
        while neck.progress < 4: #1 progress for each NC/superlikely, 1 for encountering 5 Dudes and 1 progress for either 8 dudes total or 1 Bob.
            neck.resolve_turn(player_state)
        while elbow.progress < 4: #1 progress for each NC/superlikely, 1 for encountering 5 Dudes and 1 progress for either 8 dudes total or 1 Bob.
            elbow.resolve_turn(player_state)
        return player_state, heart, neck, elbow

    def run_simulator(self, iterations = 1000):
        turns = []
        banishes = []
        superlikelies = []

        for a in range(iterations):
            player_state, heart, neck, elbow = self.do_quest(PlayerState())
            turns.append(player_state.get_total_turns_spent())
            pity1 = heart.get_superlikelies_encountered()
            pity2 = heart.get_superlikelies_encountered()
            pity3 = neck.get_superlikelies_encountered()
            total_pity = pity1 + pity2 + pity3
            superlikelies.append(total_pity)

        Utils.log("In {} instances at {}% +NC, an average of {} pity NCs with {} turns between, it took an average of {} turns to complete the quest, with a median of {} and a deviation of {}."
        .format(iterations, PlayerState().player_nc, statistics.mean(superlikelies), heart.get_pity_cooldown(), statistics.mean(turns), statistics.median(turns), statistics.pstdev(turns)))


class PlayerState():

    def __init__(self):
        self.player_nc = 29 # Change your current +non-combat% modifier here.
        self.player_item = 200 # Change your current +item% modifier here.
        self.total_turns_spent = 0
        self.wishes = 3
        self.banishes = [ #"Banish Name", duration, max_available_uses, has_cooldown, is_free
                            Banisher("Spring Bumper", 30, 999, True, True), #Add number of banishes in a variable
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
        self.tracked_phylum = "Dude"
        self.olfacted_mob = None
        self.latted_mob = None
        self.mated_mob = None
        self.inventory = {
                            "ketchup hound": 0,
                            "another item": 0,
                            "disposable instant camera": 1,
                            "photograph of a dog": 0,
                            "I Love Me, Vol. I": 0,
                            "photograph of a red nugget": 0,
                            "photograph of an ostrich egg": 0,
                            "photograph of God": 0
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

    def get_banishes(self):
        return self.banishes

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

    def choose_banish(self, encounter):
        avail_banish = None
        for banish in self.banishes:
            if banish.get_banished_mob(self) == encounter.get_name():
                return False
            if (not avail_banish) and banish.check(self):
                avail_banish = banish
                return avail_banish
        return avail_banish

    def check_banish(self, location, encounter):
        if location.get_banishes_left():
            banish = self.choose_banish(encounter)
            if banish:
                banish.use(location, self, encounter)
                return True
        return False

    def mod_cap(virgin_mod):
        if virgin_mod < 0:
            return 0
        if virgin_mod > 25:
            return 20 + math.floor(virgin_mod/5)
        return virgin_mod


class Copier():

    def __init__(self, name = "", length = 30, avail_uses = 3, cooldown = False, copies = 1, rejection = True):
        self.name = name
        self.length = length
        self.avail_uses = avail_uses
        self.cooldown = cooldown
        self.copies = copies
        self.rejection = rejection
        self.copied_mob = None
        self.expiry = -1

    def get_avail_uses(self):
        return self.avail_uses

    def get_copies(self):
        return self.copies

    def get_copied_mob(self, player_state):
        if self.get_expiry() < player_state.get_total_turns_spent():
            if not self.rejection:
                player_state.reset_olfacted_mob()
            return None
        return self.copied_mob

    def get_expiry(self):
        return self.expiry

    def check(self, player_state):
        return (self.get_avail_uses()) and (self.get_expiry() < player_state.get_total_turns_spent())

    def use(self, location, player_state, encounter):
        name = encounter.get_name()
        self.copied_mob = name
        self.avail_uses -= 1
        self.expiry = player_state.get_total_turns_spent() + self.length
        if not self.rejection:
            player_state.set_olfacted_mob(name)


class Banisher():

    def __init__(self, name = "", length = 30, avail_uses = 3, cooldown = False, free = True):
        self.name = name
        self.length = length
        self.avail_uses = avail_uses
        self.cooldown = cooldown
        self.free = free
        self.banished_mob = None
        self.expiry = -1

    def get_avail_uses(self):
        return self.avail_uses

    def get_expiry(self):
        return self.expiry

    def get_banished_mob(self, player_state):
        if self.get_expiry() < player_state.get_total_turns_spent():
            return None
        return self.banished_mob

    def check(self, player_state):
        return (self.get_avail_uses()) and (self.get_expiry() < player_state.get_total_turns_spent())

    def use(self, location, player_state, encounter):
        self.banished_mob = encounter.get_name()
        self.avail_uses -= 1
        self.expiry = player_state.get_total_turns_spent() + self.length
        if self.free:
            location.toggle_free_turn()
        location.incr_banishes_used()


class Encounter():

    def __init__(self, name = "", phylum = None, banish = False, copy = False):
        self.name = name
        self.phylum = phylum
        self.wish = False
        self.should_banish = banish
        self.should_copy = copy

    def __str__(self):
        return "Encounter({})".format(self.name)

    def get_name(self):
        return self.name

    def get_phylum(self):
        return self.phylum

    def get_use_all_sniffs(self):
        return self.use_all_sniffs

    def check(self, player_state):
        for banish in player_state.get_banishes():
            if banish.get_banished_mob(player_state) == self.name:
                return False
        return True

    def add_nc_queue(self, location, nc = None):
        if nc is None:
            nc = self.name
        location.append_nc_history(nc)

    def add_com_queue(self, location, combat = None):
        if combat is None:
            combat = self.name
        location.append_combat_history(combat)

    def run(self, location, player_state):
        if self.should_banish:
            player_state.check_banish(location, self)
        if self.should_copy:
            player_state.check_copier(location, self)
        self.add_com_queue(location)
        if location.get_free_turn():
            location.toggle_free_turn()
            return True
        location.incr_turns_spent()
        player_state.incr_total_turns_spent()


class Location():

    def __init__(self, native_nc, superlikelies, non_combats, combats, banishes_to_commit=0, pity_cooldown=0):
        self.native_nc = native_nc
        self.superlikelies = superlikelies
        self.non_combats = non_combats
        self.combats = combats
        self.nc_history = collections.deque([], 5)
        self.combat_history = collections.deque([], 5)
        self.banishes_to_commit = banishes_to_commit
        self.pity_cooldown = pity_cooldown
        self.banishes_used = 0
        self.free_turn = False
        self.turns_spent = 0

    def get_non_combats(self):
        return self.non_combats

    def get_free_turn(self):
        return self.free_turn

    def get_banishes_used(self):
        return self.banishes_used

    def incr_banishes_used(self):
        self.banishes_used += 1

    def get_pity_cooldown(self):
        return self.pity_cooldown

    def get_turns_spent(self):
        return self.turns_spent

    def incr_turns_spent(self):
        self.turns_spent += 1

    def select_encounter(self, player_state):
        encounter = self.select_superlikely(player_state)
        if encounter is None:
            encounter = self.select_nc(player_state)
        if encounter is None:
            encounter = self.select_combat(player_state)
        return encounter

    def select_superlikely(self, player_state):
        for superlikely in self.superlikelies:
            if superlikely.check(self, player_state):
                return superlikely
        return None

    def append_nc_history(self, nc):
        self.nc_history.append(nc)

    def append_combat_history(self, combat):
        self.combat_history.append(combat)

    def weighted_random(self, weights):
        total = sum(weight for item, weight in weights.items())
        if not total:
            return None
        r = random.randint(1, total)
        for (item, weight) in weights.items():
            r -= weight
            if r <= 0:
                return item

    def get_nc_weights(self, player_state):
        nc_weights = {}
        for encounter in [nc for nc in self.non_combats if nc.check(self, player_state)]:
            name = encounter.get_name()
            copies = 1 #+ (player_state.get_extra_copies(encounter) if name not in nc_weights.keys() else 0) #I have not sorted this yet.
            nc_weights[name] = copies if name in self.nc_history else (4 * copies)
        return nc_weights

    def select_nc(self, player_state):
        if not len(self.non_combats):
            return None
        actual_nc = self.native_nc + player_state.get_player_nc()
        if actual_nc == 0:
            return None
        if random.randrange(100) > actual_nc:
            return None
        encounter_name = self.weighted_random(self.get_nc_weights(player_state))
        if encounter_name:
            return [nc for nc in self.non_combats if nc.name == encounter_name][0]
        return None

    def get_combat_weights(self, player_state):
        combat_weights = {}
        for encounter in [monster for monster in self.combats if monster.check(player_state)]:
            name = encounter.get_name()
            copies = 1 + (player_state.get_extra_copies(encounter) if name not in combat_weights.keys() else 0)
            combat_weights[name] = copies if (name in self.combat_history and not player_state.get_olfacted_mob() == name) else (4 * copies)
        return combat_weights

    def select_combat(self, player_state):
        encounter_name = self.weighted_random(self.get_combat_weights(player_state))
        return [combat for combat in self.combats if combat.name == encounter_name][0]
        return None

    def toggle_free_turn(self):
        self.free_turn = not self.free_turn

    def resolve_turn(self, player_state):
        encounter = None
        loops = 0
        while (encounter is None) and (loops < 100):
            encounter = self.select_encounter(player_state)
            loops += 1
        if encounter is not None:
            encounter.run(self, player_state)
            #Verbose information underneath
            #print("{}: {} at {} progress.".format(player_state.get_total_turns_spent(), encounter.get_name(), self.get_progress()))


class FriarLoc(Location):

    class PityNC(Encounter):

        def __init__(self, name = ""):
            self.name = name

        def check(self, location, player_state):
            #return location.get_turns_spent() == 10 or (location.get_pity_timer() > (location.get_pity_cooldown() - random.randint(1,2)))
            return location.get_pity_timer() == location.get_pity_cooldown()

        def run(self, location, player_state):
            location.incr_superlikelies()
            nc = location.get_non_combats()
            nc[0].run(location, player_state)


    class ProgressNC(Encounter):

        def __init__(self, name = ""):
            self.name = name

        def check(self, location, player_state):
            return True

        def run(self, location, player_state):
            location.incr_turns_spent()
            location.incr_progress()
            location.set_pity_timer(1)
            player_state.incr_total_turns_spent()


    class Combat(Encounter):

        def run(self, location, player_state):
            self.add_com_queue(location)
            location.incr_pity_timer()
            if self.should_banish:
                player_state.check_banish(location, self)
            if self.should_copy:
                player_state.check_copier(location, self)
            if location.get_free_turn():
                location.toggle_free_turn()
                return True
            location.incr_turns_spent()
            player_state.incr_total_turns_spent()


    def __init__(self):
        Location.__init__(
            self,
            5, #Native Non-Combat rate of location
            [   #Superlikelies go here
                FriarLoc.PityNC("Pity NC")
            ],
            [   #NCs go here
                FriarLoc.ProgressNC("Progress NC")
            ],
            [   #"Combat Name", "Phylum", should_banish, should_sniff
                FriarLoc.Combat("Imp 1", "Demon", False, False),
                FriarLoc.Combat("Imp 2", "Demon", False, False),
                FriarLoc.Combat("Imp 3", "Demon", False, False)
            ],
            0, #Number of banishes to commit to the location
            4 #Turns between each pity
        )
        self.progress = 0
        self.pity_timer = 0
        self.quest_items = 0
        self.dudes_fought = 0
        self.superlikelies_encountered = 0

    def get_banishes_left(self):
        return self.banishes_used < self.banishes_to_commit

    def get_progress(self):
        return self.progress

    def incr_progress(self):
        self.progress += 1

    def get_pity_timer(self):
        return self.pity_timer

    def incr_pity_timer(self):
        self.pity_timer += 1

    def set_pity_timer(self, value):
        self.pity_timer = value

    def reset_pity_timer(self):
        self.pity_timer = 0

    def get_superlikelies_encountered(self):
        return self.superlikelies_encountered

    def incr_superlikelies(self):
        self.superlikelies_encountered += 1

if __name__ == "__main__":
    Simulator().run_simulator()
