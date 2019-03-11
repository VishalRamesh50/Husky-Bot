import unittest
from unittest.mock import MagicMock
from hours import Hours
from discord.ext import commands
import NUDining

client = commands.Bot(command_prefix='.')


class TestHours(unittest.TestCase):

    def setUp(self):
        self.hoursClass = Hours(client)
        MagicMock().day = ''
        MagicMock().comma = False
        MagicMock().content = ''

    def tearDown(self):
        pass

    def test_determinePeriod(self):
        self.assertEqual(self.hoursClass.determinePeriod(12), 'PM')
        self.assertEqual(self.hoursClass.determinePeriod(0), 'AM')
        self.assertEqual(self.hoursClass.determinePeriod(6), 'AM')
        self.assertEqual(self.hoursClass.determinePeriod(18), 'PM')
        self.assertEqual(self.hoursClass.determinePeriod(24), 'PM')
        self.assertEqual(self.hoursClass.determinePeriod(25), 'AM')

    def test_isAlias(self):
        self.assertEqual(self.hoursClass.isAlias("STWEST", NUDining.MLK_LOCATIONS), True)
        self.assertEqual(self.hoursClass.isAlias("GYRO", NUDining.MLK_LOCATIONS), False)
        self.assertEqual(self.hoursClass.isAlias("STWEST", NUDining.PRESIDENTS_LOCATIONS), True)
        self.assertEqual(self.hoursClass.isAlias("GYRO", NUDining.PRESIDENTS_LOCATIONS), False)
        self.assertEqual(self.hoursClass.isAlias("STWEST", NUDining.SPRING_BREAK_LOCATIONS), True)
        self.assertEqual(self.hoursClass.isAlias("GYRO", NUDining.SPRING_BREAK_LOCATIONS), False)
        self.assertEqual(self.hoursClass.isAlias("STWEST", NUDining.NORMAL_LOCATIONS), True)
        self.assertEqual(self.hoursClass.isAlias("GYRO", NUDining.NORMAL_LOCATIONS), True)


if __name__ == '__main__':
    unittest.main()
