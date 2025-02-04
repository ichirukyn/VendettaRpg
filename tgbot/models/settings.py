from xmlrpc.client import boolean

setting_list = [
    {"label": "Включить всё", "attr": "all"},
    {"label": "Подтверждение техник", "attr": "confirm_technique"},
    {"label": "Подтверждение заклинаний", "attr": "confirm_spell"},
    {"label": "Подтверждение паса", "attr": "confirm_pass"},
    {"label": "Подтверждение побега", "attr": "confirm_escape"},
    {"label": "Подтверждение использования предметов", "attr": "confirm_battle_item"},
    {"label": "Максимум слотов: {}", "attr": "slot_count", "value": 6, "value_list": [4, 6, 8]},
    # {"label": "Подтверждение Выброса предмета", "attr": "confirm_escape"},
]


class Settings:
    def __init__(self):
        self.all = False
        self.confirm_technique = False
        self.confirm_spell = False
        self.confirm_pass = False
        self.confirm_escape = True
        self.confirm_battle_item = False
        self.slot_count = 6

    def filter(self, name='all', val=None):
        for setting in setting_list:
            attr = setting.get('attr', '')

            if name == 'all' or name == attr:
                value = getattr(self, attr)

                if isinstance(value, boolean):
                    value = not value

                list = setting.get('value_list', None)

                if list is not None:
                    index = list.index(value)
                    value = list[index + 1] if index < len(list) - 1 else list[0]

                if val is not None:
                    value = val

                if hasattr(self, attr):
                    setattr(self, attr, value)
                    return value

    def active_all(self):
        self.filter('all', True)

    def deactivate_all(self):
        self.filter('all', False)
