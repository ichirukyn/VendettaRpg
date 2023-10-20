class EntityResist:
    fire_resist = 0
    water_resist = 0
    earth_resist = 0
    air_resist = 0
    light_resist = 0
    dark_resist = 0
    phys_resist = 0

    ignore_resist = 0

    def init_resist(self, fire_resist, water_resist, earth_resist, air_resist, light_resist, dark_resist, phys_resist):
        self.fire_resist = fire_resist
        self.water_resist = water_resist
        self.earth_resist = earth_resist
        self.air_resist = air_resist
        self.light_resist = light_resist
        self.dark_resist = dark_resist
        self.phys_resist = phys_resist
