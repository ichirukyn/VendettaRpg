from collections import namedtuple

SkillTypeTuple = namedtuple("SkillType", ["attack", "support"])
SkillType = SkillTypeTuple("attack", "support")

SkillDirectionTuple = namedtuple("SkillDirection", ["my", "enemy", "teammate", "enemies", "teammates"])
SkillDirection = SkillDirectionTuple("my", "enemy", "teammate", "enemies", "teammates")

SkillSubActionTuple = namedtuple("SkillDirection", ["evasion", "defense", "counter_strike", "escape"])
SkillSubAction = SkillSubActionTuple("evasion", "defense", "counter_strike", "escape")
