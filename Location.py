import collections
import random

class Location():

    def __init__(self, native_nc, superlikelies, non_combats, combats, delay=0, banishers_to_commit=0):
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
        self.macrod = False
        self.add_queue = True
        self.free_turn = False
        self.quest_items = 0
        self.dudes_fought = 0 # Add other phylums later

    # Turns spent
    def get_turns_spent(self):
        return self.turns_spent

    def incr_turns_spent(self):
        self.turns_spent += 1

    # Progress
    def get_progress(self):
        return self.progress

    def incr_progress(self):
        self.progress += 1

    # Pity timer
    def get_pity_timer(self):
        return self.pity_timer

    def incr_pity_timer(self):
        self.pity_timer += 1

    def reset_pity_timer(self):
        self.pity_timer = 0

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

    def reset_add_queue(self):
        if not self.add_queue:
            self.add_queue = True

    # Macrometeorite
    def get_macrod(self):
        return self.macrod

    def reset_macrod(self):
        self.macrod = False

    # Free turns
    def get_free_turn(self):
        return self.free_turn

    def toggle_free_turn(self):
        self.free_turn = not self.free_turn

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
        for encounter in [monster for monster in self.combats if monster.check(self, player_state)]:
            name = encounter.get_name()
            copies = 1 + (player_state.get_extra_copies(encounter) if name not in combat_weights.keys() else 0)
            combat_weights[name] = copies if (name in self.combat_history and not player_state.get_olfacted_mob() == name) else (4 * copies)
        return combat_weights

    def select_combat(self, player_state):
        encounter_name = self.weighted_random(self.get_combat_weights(player_state))
        return [combat for combat in self.combats if combat.name == encounter_name][0]
        return None

    def select_macro_combat(self, player_state, monster):
        self.macrod = True
        encounters = []
        for combat in self.combats:
            if combat.check(self, player_state) and (combat.get_name() != monster.get_name()):
                encounters.append(combat)
        return encounters[random.randrange(len(encounters))].run(self, player_state) # Needs tumbleweed handling

    def resolve_turn(self, player_state, location):
        encounter = None
        loops = 0
        while (encounter is None) and (loops < 100):
            encounter = self.select_encounter(player_state)
            loops += 1
        if encounter is not None:
            encounter.run(self, player_state)
