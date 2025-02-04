from collections import namedtuple

ItemTypeList = ["weapon", "money", "support", "potion_hp", "potion_mp", "potion_qi"]

ItemTypeTuple = namedtuple("ItemType", ItemTypeList)
ItemType = ItemTypeTuple(*ItemTypeList)

SkillDirectionTuple = namedtuple("SkillDirection", ["my", "enemy", "teammate", "enemies", "teammates"])
SkillDirection = SkillDirectionTuple("my", "enemy", "teammate", "enemies", "teammates")

SkillSubActionTuple = namedtuple("SkillDirection", ["evasion", "defense", "counter_strike", "escape"])
SkillSubAction = SkillSubActionTuple("evasion", "defense", "counter_strike", "escape")
