import unittest
import sys
sys.path.append('src')
from hours_model import HoursModel  # noqa: E402
from unittest.mock import Mock, patch  # noqa: E402
from datetime import datetime  # noqa: E402


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


# TODO: Figure out a way to mock some data so result is not variable on when the test suite is run
# NOTE: These should work during normal Fall Hours
class TestObtainHoursKeyValue(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.obtain_hours_key_value = self.model._HoursModel__obtain_hours_key_value

    def test_valid_location_and_day_full_all_caps(self):
        expected = ('MTWR', [11, 0, 20, 0])
        self.assertEqual(self.obtain_hours_key_value('STETSON WEST', 'MONDAY'), expected)

    def test_invalid_location(self):
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'test', 'monday')

    def test_day_empty_string(self):
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'stwest', '')

    def test_both_empty_string(self):
        self.assertRaises(AssertionError, self.obtain_hours_key_value, '', '')

    def test_case_insensitive_acronyms(self):
        expected = ('F', [7, 0, 22, 0])
        self.assertEqual(self.obtain_hours_key_value('sTEast', 'friDAY'), expected)

    def test_whitespace_around_location(self):
        expected = ('F', [7, 0, 22, 0])
        self.assertEqual(self.obtain_hours_key_value('  sTEast  ', 'friDAY'), expected)

    def test_whitespace_around_day(self):
        expected = ('F', [7, 0, 22, 0])
        self.assertEqual(self.obtain_hours_key_value('STEAST', '  FRIDAY  '), expected)

    def test_whitespace_between_location(self):
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'S TE A ST', 'FRIDAY')

    def test_whitespace_between_day(self):
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'STEAST', 'F R ID AY')

    def test_closed_location(self):
        expected = ('S', [-1, -1, -1, -1])
        self.assertEqual(self.obtain_hours_key_value('stwest', 'SATURDAY'), expected)


class TestObtainTimes(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.obtain_times = self.model._HoursModel__obtain_times

    def test_obtaining_time_normal(self):
        self.assertEqual(self.obtain_times(('MTWR', [11, 0, 20, 0])), [11, 0, 20, 0])

    def test_obtaining_time_invalid_list_length(self):
        self.assertRaises(AssertionError, self.obtain_times, ('MTWR', [11, 0, 20, 0, 1]))

    def test_closed_location(self):
        self.assertEqual(self.obtain_times(('S', [-1, -1, -1, -1])), [-1, -1, -1, -1])


class TestObtainDayRange(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.obtain_day_range = self.model._HoursModel__obtain_day_range

    def test_single_day(self):
        input = ('T', [11, 0, 20, 0])
        expected = 'TUESDAY'
        self.assertEqual(self.obtain_day_range(input), expected)

    def test_two_days(self):
        input = ('TW', [11, 0, 20, 0])
        expected = 'TUESDAY-WEDNESDAY'
        self.assertEqual(self.obtain_day_range(input), expected)

    def test_day_range_acronym_not_first_letter_of_day(self):
        input = ('MTWR', [11, 0, 20, 0])
        expected = 'MONDAY-THURSDAY'
        self.assertEqual(self.obtain_day_range(input), expected)

    def test_day_empty_string(self):
        input = ('', [11, 0, 20, 0])
        self.assertRaises(AssertionError, self.obtain_day_range, input)

    # this method will get the correct day range regardless of whether the other data is valid
    def test_invalid_time_list(self):
        input = ('FS', [])
        expected = 'FRIDAY-SATURDAY'
        self.assertEqual(self.obtain_day_range(input), expected)

    def test_closed_location(self):
        input = ('FS', [-1, -1, -1, -1])
        expected = 'FRIDAY-SATURDAY'
        self.assertEqual(self.obtain_day_range(input), expected)

    def test_whitespace_between_days(self):
        input = ('U   W', [])
        expected = 'SUNDAY-WEDNESDAY'
        self.assertEqual(self.obtain_day_range(input), expected)

    def test_whitespace_around_days(self):
        input = ('  UW  ', [])
        expected = 'SUNDAY-WEDNESDAY'
        self.assertEqual(self.obtain_day_range(input), expected)

    def test_whitespace_around_and_between_days(self):
        input = ('  U   W  ', [])
        expected = 'SUNDAY-WEDNESDAY'
        self.assertEqual(self.obtain_day_range(input), expected)


class TestDeterminePeriod(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.determine_period = self.model._HoursModel__determine_period

    def test_negative(self):
        self.assertRaises(AssertionError, self.determine_period, -1)

    def test_zero(self):
        self.assertEqual(self.determine_period(0), 'AM')

    def test_early_morning(self):
        self.assertEqual(self.determine_period(2), 'AM')

    def test_twelve_pm(self):
        self.assertEqual(self.determine_period(12), 'PM')

    def test_afternoon(self):
        self.assertEqual(self.determine_period(17), 'PM')

    def test_midnight(self):
        self.assertEqual(self.determine_period(24), 'AM')

    def test_past_24_hour_time(self):
        self.assertEqual(self.determine_period(25), 'AM')

    def test_past_48_hour_time(self):
        self.assertEqual(self.determine_period(49), 'AM')


class TestLocationMsg(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    def test_location_day_all_caps(self):
        location = "STETSON WEST"
        day = "MONDAY"
        expected = "STETSON WEST is open from 11:00 AM - 8:00 PM on MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    def test_location_acronym_day_all_caps(self):
        location = "STWEST"
        day = "MONDAY"
        expected = "STWEST is open from 11:00 AM - 8:00 PM on MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    def test_location_day_mixed_case(self):
        location = "sTwEsT"
        day = "MonDaY"
        expected = "STWEST is open from 11:00 AM - 8:00 PM on MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    def test_location_with_apostrophe_mixed_case(self):
        location = "cappy's"
        day = "tuesday"
        expected = "CAPPY'S is open from 6:30 AM - 2:00 AM on MONDAY-SUNDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    def test_location_closed_on_day(self):
        location = "stwest"
        day = "SATURDAY"
        expected = "STWEST is CLOSED SATURDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)


class TestOpen(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_location_open(self, datetime_mock):
        # Mock Date: Nov 23, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertEqual(self.model.open(location, day), False)

    @patch('hours_model.datetime')
    def test_location_closed_on_day(self, datetime_mock):
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.open(location, day), True)

    @patch('hours_model.datetime')
    def test_checking_if_open_different_day(self, datetime_mock):
        # Mock Date: Nov 24, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        location = "STETSON WEST"
        day = "SUNDAY"
        # says it's closed since it's Saturday not Sunday
        # even though it would be open on Sunday at this time
        self.assertEqual(self.model.open(location, day), False)


class TestTimeTillOpen(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_location_open_in_half_hour(self, datetime_mock):
        # Mock Date: Nov 24, 2019 3:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 30)

    @patch('hours_model.datetime')
    def test_location_closed_entire_day(self, datetime_mock):
        # Mock Date: Nov 24, 2019 3:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 15, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        location = "STETSON WEST"
        day = "SUNDAY"
        # should not be 30 mins till open since it won't be open until the next day
        self.assertNotEqual(self.model.time_till_open(location, day), 30)
        # should be equal to 24 hours + 30 mins to be opening at 4:30pm on Sunday
        self.assertEqual(self.model.time_till_open(location, day), 1470)

    @patch('hours_model.datetime')
    def test_location_already_open(self, datetime_mock):
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 0)

class TestGetLink(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    def test_get_link_full_name(self):
        link = "https://nudining.com/hours"
        self.assertEqual(link, self.model.get_link('stetson west'))

    def test_get_link_alias(self):
        link = "https://nudining.com/hours"
        self.assertEqual(link, self.model.get_link('stwest'))
    
    def test_get_non_northeastern_location(self):
        link = "http://www.bostonshawarma.net"
        self.assertEqual(link, self.model.get_link('boston shawarma'))


if __name__ == '__main__':
    unittest.main()
