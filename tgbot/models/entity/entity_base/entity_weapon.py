class EntityWeapon:
    weapon_name = ''
    weapon_desc = ''
    weapon_lvl = 0
    weapon_modify = 0
    weapon_damage = 1

    def add_weapon(self, weapon, lvl):
        self.weapon_name = weapon['name']
        self.weapon_desc = weapon['desc']
        self.weapon_modify = weapon['modify']
        self.weapon_lvl = lvl

        lvl_atk = self.weapon_modify * self.weapon_lvl

        self.weapon_damage = weapon['value'] * lvl_atk if lvl_atk > 0 else weapon['value']
