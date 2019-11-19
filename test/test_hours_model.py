import unittest
import sys
sys.path.append('src')
from hoursModel import HoursModel  # noqa: E402


class TestValidLocation(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    # test that main words exactly as stored are recognized (one word)
    def test_recognized_location_exact_all_caps_one_word(self):
        self.assertTrue(self.model.valid_location("OUTTAKES"))

    # test that main words exactly as stored are recognized (two words)
    def test_recognized_location_exact_all_caps_two_words(self):
        self.assertTrue(self.model.valid_location("INTERNATIONAL VILLAGE"))

    # test that main words exactly as stored are recognized (one word & lowercase)
    def test_recognized_location_all_lowercase_one_word(self):
        self.assertTrue(self.model.valid_location("outtakes"))

    # test that main words exactly as stored are recognized (two words & mixed case)
    def test_recognized_location_mixed_case_two_words(self):
        self.assertTrue(self.model.valid_location("inTernAtional vIllAge"))

    # testing that another alias is still recognized
    def test_recognized_location_alias_lowercase_one_word(self):
        self.assertTrue(self.model.valid_location("stwest"))

    # testing that names with single apostrophes work
    def test_recognized_location_alias_lowercase_with_special_chars(self):
        self.assertTrue(self.model.valid_location("cappy's"))

    # testing that name which doesn't exist will not work
    def test_unrecognized_location_one_word(self):
        self.assertFalse(self.model.valid_location("test"))


class TestValidDay(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    # test that an all caps valid day is recognized
    def test_valid_day_exact_all_caps(self):
        self.assertTrue(self.model.valid_day("MONDAY"))

    # test that a lowercase valid day is recognized
    def test_valid_day_all_lowercase(self):
        self.assertTrue(self.model.valid_day("tuesday"))

    # test that a mixed case valid day is recognized
    def test_valid_day_mixed_case(self):
        self.assertTrue(self.model.valid_day("SUNday"))

    # test that an invalid day is not recognized
    def test_invalid_day(self):
        self.assertFalse(self.model.valid_day("munday"))

    # test that day acronyms is invalid (might include this later)
    def test_invalid_day_acronym(self):
        self.assertFalse(self.model.valid_day("sat"))


if __name__ == '__main__':
    unittest.main()
