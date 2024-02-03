class EntityWeapon:
    weapon_name = ''
    weapon_desc = ''
    weapon_lvl = 0
    weapon_modify = 0
    weapon_damage = 1

    def init_weapon(self, weapon, lvl):
        self.weapon_name = weapon['name']
        self.weapon_desc = weapon['desc']
        self.weapon_modify = weapon['modify']
        self.weapon_damage = weapon['value']
        self.weapon_lvl = lvl

        if self.weapon_lvl > 0:
            self.weapon_damage = weapon['value'] + self.weapon_modify * self.weapon_lvl

        return self
