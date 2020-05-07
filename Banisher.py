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
        location.incr_banishers_used()
