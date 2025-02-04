class ItemFactory:
    @staticmethod
    def item(data):
        id = data.get('item_id')
        name = data.get('name', '')
        desc = data.get('desc', '')
        value = data.get('value', 0)
        type = data.get('type')
        modify = data.get('modify', 0)
        race_id = data.get('race_id', 0)
        class_id = data.get('class_id', 2)
        class_type = data.get('class_type', False)
        item_id = data.get('item_id', 0)
        count = data.get('count', 0)

        return Item(id, name, desc, type, race_id, value, modify, class_id, class_type, item_id, count)


class Item:
    def __init__(self, id, name, desc, type, race_id, value, modify, class_id, class_type, item_id, count):
        self.id = id
        self.name = name
        self.desc = desc
        self.type = type
        self.race_id = race_id
        self.value = value
        self.modify = modify
        self.class_id = class_id
        self.class_type = class_type
        self.item_id = item_id
        self.count = count
        self.log = None

    def check(self, entity) -> bool:
        if entity.potion_cd > 0:
            self.log = f"Вы уже использовали зелья в этом ходу"
            return False

        match self.type:
            case 'potion_hp':
                if entity.hp >= entity.hp_max:
                    self.log = f"У вас полные hp"
                    return False
            case 'potion_mp':
                if entity.mp >= entity.mp_max:
                    self.log = f"У вас полные mp"
                    return False
            case 'potion_qi':
                if entity.qi >= entity.qi_max:
                    self.log = f"У вас полные qi"
                    return False

        return True

    def activate(self, entity, target=None) -> str:
        match self.type:
            case 'potion_hp':
                entity.hp += self.value

                if entity.hp > entity.hp_max:
                    entity.hp = entity.hp_max
            case 'potion_mp':
                entity.mp += self.value

                if entity.mp > entity.mp_max:
                    entity.mp = entity.mp_max
            case 'potion_qi':
                entity.qi += self.value

                if entity.qi > entity.qi_max:
                    entity.qi = entity.qi_max

        return f"Использовано {self.name}"

    def deactivate(self, entity) -> str:
        return "Ок-с.."


def item_init(item_db):
    try:
        # for bonus in item_db.get('effects', []):
        #     new_bonuses.append(EffectFactory.create_effect(bonus, source=('Item', item_db.get('item_id', 0))))

        item = ItemFactory.item(item_db)

        return item
    except KeyError as e:
        print(e)
        return None
