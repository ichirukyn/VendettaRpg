setting_list = [
    {"label": "Включить всё", "value": "all"},
    {"label": "Подтверждение техник", "value": "confirm_technique"},
    {"label": "Подтверждение заклинаний", "value": "confirm_spell"},
    {"label": "Подтверждение Паса", "value": "confirm_pass"},
    {"label": "Подтверждение Побега", "value": "confirm_escape"},
    # {"label": "Подтверждение Выброса предмета", "value": "confirm_escape"},
]


class Settings:
    def __init__(self):
        self.all = False
        self.confirm_technique = False
        self.confirm_spell = False
        self.confirm_pass = False
        self.confirm_escape = True

    def filter(self, name='all', val=None):
        for setting in setting_list:
            attr = setting.get('value', '')

            if name == 'all' or name == attr:
                boolean = not getattr(self, attr)

                if val is not None:
                    boolean = val

                if hasattr(self, attr):
                    setattr(self, attr, boolean)

    def active_all(self):
        self.filter('all', True)

    def deactivate_all(self):
        self.filter('all', False)
