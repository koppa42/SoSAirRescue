from ..aircraft import Aircraft, AircraftAbility

Mi26 = Aircraft(2.10, 'Mi-26 基本型', AircraftAbility("Freight", "Hanging", "Manned", "Fire"), 805, 805, 12000, 255, 3000, 82, 20000, 15000,
                fuel_fill_time=1200, person_on_off_time=60, supply_load_time=0.1, device_load_time=1200, water_weight=15, 
                water_load_time=900, extinguishing_time=900)
Mi171 = Aircraft(0.46, 'Mi-171 基本型', AircraftAbility("Freight", "Manned", "Winch", "Fire"), 356, 356, 1700, 240, 1175, 26, 4000, 3000,
                 water_weight=3)
AC313 = Aircraft(1.00, 'AC313 基本型', AircraftAbility("Freight", "Manned", "Winch", "Fire"), 281, 281, 3500, 251, 1065, 27, 4000, 5000,
                 water_weight=5)
AC313Medical = Aircraft(1.10, 'AC313 医疗型', AircraftAbility("Freight", "Manned", "Winch", "Medical"), 281, 281, 3500, 251, 1065, 9, 2000, 5000,
                        supply_load_time=0.2)
H225 = Aircraft(1.86, 'H225 救援型', AircraftAbility("Freight", "Manned", "Winch", "Sea"), 207, 207, 2336, 276, 559, 19, 2200, 4500,
                supply_load_time=0.2)
H225Medical = Aircraft(1.92, 'H225 医疗型', AircraftAbility("Freight", "Manned", "Winch", "Medical", "Sea"), 207, 207, 2326, 276, 559, 6, 2200, 4500,
                       supply_load_time=0.2)
AC352 = Aircraft(1.20, 'AC352 基本型', AircraftAbility("Reconnoitre", "Freight", "Manned", "Winch", "Fire", "Sea"), 172, 172, 2066, 244, 533, 15, 1200, 3000,
                 search_time=10.68)
S76 = Aircraft(0.90, 'S-76 搜救型', AircraftAbility("Reconnoitre", "Freight", "Manned", "Winch", "Sea"), 141, 141, 818, 269, 273, 13, 1100, 2300,
               search_time=12.76)
H155 = Aircraft(0.70, 'H155 搜救型', AircraftAbility("Reconnoitre", "Freight", "Manned", "Winch", "Sea"), 125, 125, 993, 280, 330, 11, 900, 1600,
                supply_load_time=0.4, search_time=15.84)
AW169 = Aircraft(0.98, 'AW169 基本型', AircraftAbility("Freight", "Manned", "Winch", "Fire", "Sea"), 116, 116, 904, 272, 220, 9, 1800, 2000,
                 water_weight=2)
AW169Medical = Aircraft(1.01, 'AW169 医疗型', AircraftAbility("Freight", "Manned", "Winch", "Medical", "Sea"), 116, 116, 904, 272, 220, 3, 900, 2000,
                        supply_load_time=0.4, patient_on_off_time=300)
AC312 = Aircraft(0.39, 'AC312 救援型', AircraftAbility("Freight", "Manned", "Winch"), 112, 112, 580, 270, 165, 12, 800, 1600,
                 supply_load_time=0.4)
AC311 = Aircraft(0.20, 'AC311 搜救型', AircraftAbility("Reconnoitre", "Freight", "Manned"), 79, 79, 423, 240, 105, 4, 500, 1000,
                 supply_load_time=0.4, search_time=13.46)
H135 = Aircraft(0.43, 'H135 医疗型', AircraftAbility("Freight", "Manned", "Medical"), 82, 82, 560, 254, 160, 2, 700, 1400,
                supply_load_time=0.4, patient_on_off_time=300)
Be11429 = Aircraft(0.26, 'Be11429 救援型', AircraftAbility("Freight", "Manned", "Winch"), 95, 95, 600, 263, 158, 6, 600, 1200,
                   supply_load_time=0.4)
ChangYing5E = Aircraft(0.24, '长鹰 5E 搜救型', AircraftAbility("Reconnoitre", "Sea"), 192, 0, 40, 180, 1, 0, 100, 300,
                       search_time=3.96, type="FixedWing")
YiLong2H = Aircraft(0.19, '翼龙 2H 搜救型', AircraftAbility("Reconnoitre"), 330, 0, 2000, 300, 100, 0, 200, 400,
                    search_time=2.58, type="FixedWing")