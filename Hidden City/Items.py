from enum import Enum

class Items(Enum):
    KetchupHound = 493
    SurgicalMask = 6684
    HeadMirror = 6685
    HalfSizeScalpel = 6686
    SurgicalApron = 6687
    AntiqueMachete = 6679
    PhotographOfGod = 2259
    BookOfMatches = 6683
    BloodiedSurgicalDungarees = 6688
    BoringBinderClip = 6694
    BowlingBall = 6696
    ShortWritOfHabeasCorpus = 6711
    ILoveMeVolI = 7262
    PhotographOfADog = 7263
    PhotographOfARedNugget = 7264
    PhotographOfAnOstrichEgg = 7265
    DisposableInstantCamera = 7266

    @classmethod
    def get_name(cls, item: "Items"):
        name = next(name for name, value in vars(cls).items() if value == item)
        new_name = ""
        for char in name:
            if char.isupper():
                char = " " + char.lower()
            new_name += char
        return new_name.lstrip()


SURGEON_GEAR = [Items.BloodiedSurgicalDungarees,
                Items.HalfSizeScalpel,
                Items.HeadMirror,
                Items.SurgicalApron,
                Items.SurgicalMask]

DUMPSTER_ITEMS = [Items.BloodiedSurgicalDungarees,
                  Items.BowlingBall,
                  Items.HalfSizeScalpel,
                  Items.HeadMirror,
                  Items.SurgicalApron,
                  Items.SurgicalMask]