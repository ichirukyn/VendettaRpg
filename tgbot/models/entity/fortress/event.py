from tgbot.models.entity.effects.effect import EffectFactory


class EventFactory:
    @staticmethod
    def create_event(data, bonuses):
        id = data.get('id', 1)
        name = data.get('name', 'Лес')
        desc = data.get('desc', 'Описание')
        text = data.get('desc', 'Описание')
        type = data.get('type', 'forest')

        keyboard = data.get('type', 'forest')
        state = data.get('type', 'forest')

        event = Event(id, name, desc, text, type, keyboard, state, bonuses)
        return event


class Event:
    def __init__(self, id, name, desc, text, type, keyboard, state, bonuses):
        self.id = id
        self.name = name
        self.desc = desc
        self.text = text
        self.type = type

        self.keyboard = keyboard
        self.state = state

        self.bonuses = bonuses
        self.effects = []
        self.rewards = []  # list id items or stats point


async def event_init(event_db):
    try:
        id = event_db.get('id')
        bonuses = event_db.get('bonuses', [])

        new_bonuses = []

        for bonus in bonuses:
            new_bonuses.append(EffectFactory.create_effect(bonus, source=('event', id)))

        event = EventFactory.create_event(event_db, new_bonuses)

        return event
    except Exception as e:
        print(f'Event Error\n{e}')
