import unittest
import sys
sys.path.append('src')
from hoursModel import HoursModel  # noqa: E402


class TestHoursModel(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    def test_valid_location(self):
        # ----------------------------------------------------------------
        # VALID EXAMPLES
        # ----------------------------------------------------------------
        # test that main words exactly as stored are recognized (one word)
        self.assertTrue(self.model.valid_location("OUTTAKES"))
        # test that main words exactly as stored are recognized (two words)
        self.assertTrue(self.model.valid_location("INTERNATIONAL VILLAGE"))
        # test that main words exactly as stored are recognized (one word & lowercase)
        self.assertTrue(self.model.valid_location("outtakes"))
        # test that main words exactly as stored are recognized (two words & mixed case)
        self.assertTrue(self.model.valid_location("inTernAtional vIllAge"))
        self.assertTrue(self.model.valid_location("popeyes"))
        # testing that another alias is still recognized
        self.assertTrue(self.model.valid_location("stwest"))
        # testing that names with single apostrophes work
        self.assertTrue(self.model.valid_location("cappy's"))
        # ----------------------------------------------------------------
        # INVALID EXAMPLES
        # ----------------------------------------------------------------
        # testing that name which doesn't exist will not work
        self.assertFalse(self.model.valid_location("test"))

    def test_valid_day(self):
        # ----------------------------------------------------------------
        # VALID EXAMPLES
        # ----------------------------------------------------------------
        # test that an all caps valid day is recognized
        self.assertTrue(self.model.valid_day("MONDAY"))
        # test that a lowercase valid day is recognized
        self.assertTrue(self.model.valid_day("tuesday"))
        # test that a mixed case valid day is recognized
        self.assertTrue(self.model.valid_day("SUNday"))
        # ----------------------------------------------------------------
        # INVALID EXAMPLES
        # ----------------------------------------------------------------
        # test that an invalid day is not recognized
        self.assertFalse(self.model.valid_day("munday"))
        # test that day acronyms is invalid (might include this later)
        self.assertFalse(self.model.valid_day("sat"))


if __name__ == '__main__':
    unittest.main()
