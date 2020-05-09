import collections
import random

verbose = True

class Location():

    def __init__(self, name, native_nc, superlikelies, non_combats, combats, delay = 0, banishers_to_commit = 0, macros_to_commit = 0):
        self.name = name
        self.turns_spent = 0
        self.progress = 0
        self.pity_timer = 0
        self.native_nc = native_nc
        self.superlikelies = superlikelies
        self.superlikelies_encountered = 0
        self.non_combats = non_combats
        self.combats = combats
        self.nc_history = collections.deque([], 5)
        self.combat_history = collections.deque([], 5)
        self.delay = delay
        self.banishers_to_commit = banishers_to_commit
        self.banishers_used = 0
        self.macros_to_commit = macros_to_commit
        self.macros_used = 0
        self.macrod = False
        self.add_queue = True
        self.free_turn = False
        self.quest_items = 0
        self.dudes_fought = 0 # Add other phylums later

    def __str__(self):
        return self.name

    # Turns spent
    def get_turns_spent(self):
        return self.turns_spent

    def incr_turns_spent(self, num=1):
        self.turns_spent += num

    # Progress
    def get_progress(self):
        return self.progress

    def incr_progress(self):
        self.progress += 1
        if verbose:
            print("Gained 1 location progress for a total of {}.".format(self.progress))

    # Pity timer
    def get_pity_timer(self):
        return self.pity_timer

    def incr_pity_timer(self):
        self.pity_timer += 1

    def set_pity_timer(self, num):
        self.pity_timer = num

    # Delay
    def get_delay(self):
        return self.delay

    # Superlikelies
    def get_superlikelies_encountered(self):
        return self.superlikelies_encountered

    def incr_superlikelies(self):
        self.superlikelies_encountered += 1

    def select_superlikely(self, player_state):
        for superlikely in self.superlikelies:
            if superlikely.check(self, player_state):
                return superlikely
        return None

    # Non-Combats
    def get_non_combats(self):
        return self.non_combats

    # Queue exception
    def get_add_queue(self):
        return self.add_queue

    def set_add_queue(self, boolean):
        self.add_queue = boolean

    # Macrometeorite
    def get_macrod(self):
        return self.macrod

    def set_macrod(self, boolean):
        self.macrod = boolean

    def get_macros_used(self):
        return self.macros_used

    def incr_macros_used(self):
        self.macros_used += 1

    def should_macro(self, player_state, monster):
        if not monster.get_should_macro():
            return False
        if player_state.get_macros() < 1:
            return False
        return self.macros_used < self.macros_to_commit

    # Free turns
    def get_free_turn(self):
        return self.free_turn

    def set_free_turn(self, boolean):
        self.free_turn = boolean

    # Banishing
    def get_banishers_used(self):
        return self.banishers_used

    def incr_banishers_used(self):
        self.banishers_used += 1

    def get_banishers_left(self):
        return self.banishers_used < self.banishers_to_commit

    # Quest items
    def get_quest_items(self):
        return self.quest_items

    def incr_quest_items(self):
        self.quest_items += 1

    def get_dudes_fought(self):
        return self.dudes_fought

    def incr_dudes_fought(self):
        self.dudes_fought += 1

    # Encounter selection
    def select_encounter(self, player_state):
        encounter = self.select_superlikely(player_state)
        if encounter is None:
            encounter = self.select_nc(player_state)
        if encounter is None:
            encounter = self.select_combat(player_state)
        return encounter

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
        for nc in self.non_combats:
            if nc.check(self, player_state):
                name = nc.get_name()
                copies = 1 # I have not sorted the ability for other copies
                if name not in self.nc_history:
                    copies = 4 * copies
                nc_weights[name] = copies
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
            for nc in self.non_combats:
                if nc.name == encounter_name:
                    return nc
        return None

    def get_combat_weights(self, player_state):
        combat_weights = {}
        for combat in self.combats:
            if combat.check(self, player_state):
                name = combat.get_name()
                copies = 1
                if name not in combat_weights.keys():
                    copies += player_state.get_extra_copies(combat)
                if name not in self.combat_history or player_state.get_olfacted_mob() == name:
                    copies = 4 * copies
                combat_weights[name] = copies
        return combat_weights

    def select_combat(self, player_state):
        encounter_name = self.weighted_random(self.get_combat_weights(player_state))
        for combat in self.combats:
            if combat.name == encounter_name:
                return combat
        return None

    def get_macro_weights(self, player_state, monster):
        combat_weights = {}
        for combat in self.combats:
            name = combat.get_name()
            if combat.check(self, player_state) and (name != monster.get_name()):
                copies = 1
                if name not in combat_weights.keys():
                    copies += player_state.get_extra_copies(combat)
                combat_weights[name] = copies
        return combat_weights

    def select_macro_combat(self, player_state, monster):
        encounter_name = self.weighted_random(self.get_macro_weights(player_state, monster)) # Ignores rejection
        for combat in self.combats:
            if combat.name == encounter_name:
                return combat

    def resolve_macro(self, player_state, monster):
        combat = self.select_macro_combat(player_state, monster)
        self.macrod = True
        self.incr_macros_used()
        player_state.decr_macros()
        if verbose:
            mob = combat.get_name()
            agreement = "some" if mob.endswith("s") else "a"
            print("{}: using Macrometeorite on {} {}, which changed it into a {}.".format(player_state.get_total_turns_spent() + 1, agreement, monster.get_name(), combat.get_name()))
        return combat.run(self, player_state)

    def resolve_turn(self, player_state):
        encounter = None
        loops = 0
        while (encounter == None) and (loops < 100):
            encounter = self.select_encounter(player_state)
            loops += 1
        if encounter != None:
            encounter.run(self, player_state)
