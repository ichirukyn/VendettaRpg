from tgbot.models.entity.effects.effect import Effect


class EffectHidden(Effect):
    def info(self, entity, skill=None):
        return ''
