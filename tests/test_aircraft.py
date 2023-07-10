import unittest
from arsim import aircraft


class TestAircraft(unittest.TestCase):
    def test_aircraft_ability(self):
        tmp1 = aircraft.AircraftAbility("Reconnoitre")
        self.assertEqual(tmp1.map, 0b1)

        tmp2 = aircraft.AircraftAbility("Reconnoitre", "Medical")
        self.assertEqual(tmp2.map, 0b10_0001)
