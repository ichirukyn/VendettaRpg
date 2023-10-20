class EntityDamage:
    fire_damage = 0
    water_damage = 0
    earth_damage = 0
    air_damage = 0
    light_damage = 0
    dark_damage = 0
    phys_damage = 0

    def init_damage(self, fire_damage, water_damage, earth_damage, air_damage, light_damage, dark_damage, phys_damage):
        self.fire_damage = fire_damage
        self.water_damage = water_damage
        self.earth_damage = earth_damage
        self.air_damage = air_damage
        self.light_damage = light_damage
        self.dark_damage = dark_damage
        self.phys_damage = phys_damage
