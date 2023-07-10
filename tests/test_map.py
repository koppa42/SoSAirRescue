import unittest
from arsim import map as m


class TestPosition(unittest.TestCase):
    def setUp(self) -> None:
        self.pos = [
            m.Position("1", 75, 75, 0, 0, 900, 0, 0, 30, 0, 3, 0),
            m.Position("2", 12.2, 12.2, 0, 0, 900, 0, 0, 30, 0, 3, 0),
            m.Position("3", 10, 10, 0, 0, 900, 0, 0, 30, 0, 3, 0),
            m.Position("3", 120, 10, 0, 0, 900, 0, 0, 30, 0, 3, 0)
        ]

    def test_distance_cal(self) -> None:
        self.assertAlmostEqual(
            m.Position.distance(self.pos[0], self.pos[1]), 7933.501372, delta=0.1
        )
        self.assertAlmostEqual(
            m.Position.distance(self.pos[0], self.pos[2]), 8228.199046, delta=0.1
        )
        self.assertAlmostEqual(
            m.Position.distance(self.pos[0], self.pos[3]), 7739.460387, delta=0.1
        )
        self.assertAlmostEqual(
            m.Position.distance(self.pos[1], self.pos[2]), 342.026112, delta=0.1
        )
        self.assertAlmostEqual(
            m.Position.distance(self.pos[1], self.pos[3]), 11681.313898, delta=0.1
        )
        self.assertAlmostEqual(
            m.Position.distance(self.pos[2], self.pos[3]), 11973.417122, delta=0.1
        )


class TestMap(unittest.TestCase):
    def setUp(self) -> None:
        self.pos = [
            m.Position("1", 75, 75, 0, 0, 900, 0, 0, 30, 0, 3, 0),
            m.Position("2", 12.2, 12.2, 0, 0, 900, 0, 0, 30, 0, 3, 0),
            m.Position("3", 10, 10, 0, 0, 900, 0, 0, 30, 0, 3, 0),
            m.Position("3", 120, 10, 0, 0, 900, 0, 0, 30, 0, 3, 0)
        ]
        self.map = m.Map(*self.pos)

    def test_getitem(self):
        tmp = self.map["1"]

        self.assertIsNotNone(tmp)
        self.assertEqual(tmp[0], self.pos[0])
        tmp2 = self.map["3"]

        self.assertIsNotNone(tmp2)
        self.assertTupleEqual(tmp2, (self.pos[2], self.pos[3]))
