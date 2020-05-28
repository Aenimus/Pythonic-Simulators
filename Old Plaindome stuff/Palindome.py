    class RedNugget(Encounter):

        def __init__(self, name = ""):
            self.name = name

        def check(self, location, player_state):
            return not player_state.get_inventory_item("photograph of a red nugget")

        def run(self, location, player_state):
            player_state.incr_inventory_item("photograph of a red nugget")
            location.incr_turns_spent()
            location.incr_progress()
            location.reset_pity_timer()
            location.incr_quest_items()
            player_state.incr_total_turns_spent()
            self.add_nc_queue(location)


    class OstrichEgg(Encounter):

        def __init__(self, name = ""):
            self.name = name

        def check(self, location, player_state):
            return not player_state.get_inventory_item("photograph of an ostrich egg")

        def run(self, location, player_state):
            player_state.incr_inventory_item("photograph of an ostrich egg")
            location.incr_turns_spent()
            location.incr_progress()
            location.reset_pity_timer()
            location.incr_quest_items()
            player_state.incr_total_turns_spent()
            self.add_nc_queue(location)


    class God(Encounter):

        def __init__(self, name = ""):
            self.name = name

        def check(self, location, player_state):
            return not player_state.get_inventory_item("photograph of God")

        def run(self, location, player_state):
            player_state.incr_inventory_item("photograph of God")
            location.incr_turns_spent()
            location.incr_progress()
            location.reset_pity_timer()
            location.incr_quest_items()
            player_state.incr_total_turns_spent()
            self.add_nc_queue(location)


    class Combat(Encounter):

        def run(self, location, player_state):
            self.add_com_queue(location)
            location.incr_pity_timer()
            if self.should_banish:
                player_state.check_banisher(location, self)
            if self.should_copy:
                player_state.check_copier(location, self)
            if location.get_free_turn():
                location.toggle_free_turn()
                return True
            location.incr_turns_spent()
            player_state.incr_total_turns_spent()


    class DrabBard(Encounter):

        def check_conditional_drops(self, location, player_state):
            photo = "photograph of a dog"
            quest_book = "I Love Me, Vol. I"
            if (location.get_dudes_fought() == 5) and (player_state.get_inventory_item(quest_book) < 1):
                player_state.incr_inventory_item(quest_book)
                location.incr_progress()

        def run(self, location, player_state):
            self.add_com_queue(location)
            location.incr_pity_timer()
            if self.should_banish:
                player_state.check_banisher(location, self)
            if self.should_copy:
                player_state.check_copier(location, self)
            if location.get_free_turn(): #This will need to be changed for free kills
                location.toggle_free_turn()
                return True
            location.incr_dudes_fought()
            self.check_conditional_drops(location, player_state)
            location.incr_turns_spent()
            player_state.incr_total_turns_spent()


    class Bobs(Encounter):

        def __init__(self, name = "", phylum = None, banisher = False, copy = False):
            super().__init__(name, phylum, banisher, copy)
            self.item_drops = {
                                "ketchup hound": 35,
                                "another item": 15
                                }

        def check_drops(self, location, player_state):
            for item in self.item_drops:
                if random.randrange(100) < (math.floor(self.item_drops.get(item)*player_state.item_mod())):
                    player_state.incr_inventory_item(item)

        def check_conditional_drops(self, location, player_state):
            photo = "photograph of a dog"
            camera = "disposable instant camera"
            quest_book = "I Love Me, Vol. I"
            if (player_state.get_inventory_item(camera) or (location.get_dudes_fought() > 7)) and (not player_state.get_inventory_item(photo)):
                player_state.decr_inventory_item(camera)
                player_state.incr_inventory_item(photo)
                location.incr_progress()
            if (location.get_dudes_fought() == 5) and (not player_state.get_inventory_item(quest_book)):
                player_state.incr_inventory_item(quest_book)
                location.incr_progress()

        def run(self, location, player_state):
            self.add_com_queue(location)
            location.incr_pity_timer()
            if self.should_banish:
                player_state.check_banisher(location, self)
            if self.should_copy:
                player_state.check_copier(location, self)
            if location.get_free_turn(): #This will need to be changed for free kills
                location.toggle_free_turn()
                return True
            location.incr_dudes_fought()
            self.check_drops(location, player_state)
            self.check_conditional_drops(location, player_state)
            location.incr_turns_spent()
            player_state.incr_total_turns_spent()


    def __init__(self):
        Location.__init__(
            self,
            15, #Native Non-Combat rate of location
            [   #Superlikelies go here
                Palindome.QuestSuperlikely("Quest Superlikely")
            ],
            [   #NCs go here
                Palindome.RedNugget("Red Nugget"),
                Palindome.OstrichEgg("Ostrich Egg"),
                Palindome.God("God")
            ],
            [   #"Combat Name", "Phylum", should_banish, should_sniff
                Palindome.Combat("Evil Olive", "Beast", True, False),
                Palindome.Combat("Stab Bat", "Beast", True, False),
                Palindome.Combat("Taco Cat", "Beast", True, False),
                Palindome.Combat("Tan Gnat", "Beast", True, False),
                Palindome.DrabBard("Drab Bard", "Dude", False, True),
                Palindome.Bobs("Racecar Bob", "Dude", False, True),
                Palindome.Bobs("Bob Racecar", "Dude", False, True)
            ],
            2 #Number of banishers to commit to the location
        )
