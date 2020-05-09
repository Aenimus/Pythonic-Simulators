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
