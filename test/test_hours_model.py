import unittest
import sys
sys.path.append('src')
from hours_model import HoursModel  # noqa: E402
from unittest.mock import Mock, patch  # noqa: E402
from datetime import datetime  # noqa: E402
import nu_dining  # noqa: E402


def set_date(given_date: datetime) -> None:
    """
    Sets the given datetime some mock values.
    The date is set to Jan 1, 2019
    """
    given_date.now = Mock(return_value=datetime(2019, 1, 1))
    given_date.side_effect = lambda *args, **kw: datetime(*args, **kw)
    given_date.strptime = datetime.strptime


class TestSetTodaysLocation(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.set_todays_location = self.model._HoursModel__set_todays_location

    # test that when setting todays_location during a special event, it changes
    @patch('hours_model.datetime')
    def test_set_todays_location_during_special_range(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 17, 2019 3:30pm (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 17, 15, 30))
        self.set_todays_location()
        # make sure that todays_locations are not equal to NORMAL LOCATIONS
        self.assertNotEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)
        # make sure that it has been set to WINTER INTERSESSION 1 Hours
        self.assertEqual(self.model.todays_locations, nu_dining.WINTER_INTERSSION1)
    
    # test that when setting todays_location during a special event on the last
    # day it occurs, it will still change even though the date is time agnostic
    @patch('hours_model.datetime')
    def test_set_todays_location_during_special_range_end_date_midday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 20, 2019 3:30pm (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 20, 15, 30))
        self.set_todays_location()
        # make sure that todays_locations are not equal to NORMAL LOCATIONS
        self.assertNotEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)
        # make sure that it has been set to WINTER INTERSESSION 1 Hours
        self.assertEqual(self.model.todays_locations, nu_dining.WINTER_INTERSSION1)
    
    # test that it still uses NORMAL_LOCATIONS when
    # the date is not during a special date range
    @patch('hours_model.datetime')
    def test_set_todays_location_during_normal_range(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 3:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 30))
        self.set_todays_location()
        # make sure that todays_locations are equal to NORMAL LOCATIONS
        self.assertEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)
    
    # test that it changes to use special hours during a special date range
    # but can revert back to NORMAL_LOCATIONS the next time a normal date is used
    @patch('hours_model.datetime')
    def test_set_todays_location_during_special_range_then_normal(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 20, 2019 3:30pm (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 20, 15, 30))
        self.set_todays_location()
        # make sure that todays_locations are not equal to NORMAL LOCATIONS
        self.assertNotEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)
        # make sure that it has been set to WINTER INTERSESSION 1 Hours
        self.assertEqual(self.model.todays_locations, nu_dining.WINTER_INTERSSION1)
        # Mock Date: Nov 24, 2019 3:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 30))
        self.set_todays_location()
        # make sure that todays_locations are equal to NORMAL LOCATIONS
        self.assertEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)


class TestValidLocation(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    # test that main words exactly as stored are recognized (one word)
    @patch('hours_model.datetime')
    def test_recognized_location_exact_all_caps_one_word(self, datetime_mock):
        set_date(datetime_mock)
        self.assertTrue(self.model.valid_location("OUTTAKES"))

    # test that main words exactly as stored are recognized (two words)
    @patch('hours_model.datetime')
    def test_recognized_location_exact_all_caps_two_words(self, datetime_mock):
        set_date(datetime_mock)
        self.assertTrue(self.model.valid_location("INTERNATIONAL VILLAGE"))

    # test that main words exactly as stored are recognized (one word & lowercase)
    @patch('hours_model.datetime')
    def test_recognized_location_all_lowercase_one_word(self, datetime_mock):
        set_date(datetime_mock)
        self.assertTrue(self.model.valid_location("outtakes"))

    # test that main words exactly as stored are recognized (two words & mixed case)
    @patch('hours_model.datetime')
    def test_recognized_location_mixed_case_two_words(self, datetime_mock):
        set_date(datetime_mock)
        self.assertTrue(self.model.valid_location("inTernAtional vIllAge"))

    # testing that another alias is still recognized
    @patch('hours_model.datetime')
    def test_recognized_location_alias_lowercase_one_word(self, datetime_mock):
        set_date(datetime_mock)
        self.assertTrue(self.model.valid_location("stwest"))

    # testing that names with single apostrophes work
    @patch('hours_model.datetime')
    def test_recognized_location_alias_lowercase_with_special_chars(self, datetime_mock):
        set_date(datetime_mock)
        self.assertTrue(self.model.valid_location("cappy's"))

    # testing that name which doesn't exist will not work
    @patch('hours_model.datetime')
    def test_unrecognized_location_one_word(self, datetime_mock):
        set_date(datetime_mock)
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

    # test that day acronyms is invalid TODO:(might include this later)
    def test_invalid_day_acronym(self):
        self.assertFalse(self.model.valid_day("sat"))


class TestObtainHoursKeyValue(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.obtain_hours_key_value = self.model._HoursModel__obtain_hours_key_value

    @patch('hours_model.datetime')
    def test_valid_location_and_day_full_all_caps(self, datetime_mock):
        set_date(datetime_mock)
        expected = ('MTWR', [11, 0, 20, 0])
        self.assertEqual(self.obtain_hours_key_value('STETSON WEST', 'MONDAY'), expected)

    @patch('hours_model.datetime')
    def test_invalid_location(self, datetime_mock):
        set_date(datetime_mock)
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'test', 'monday')

    @patch('hours_model.datetime')
    def test_day_empty_string(self, datetime_mock):
        set_date(datetime_mock)
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'stwest', '')

    @patch('hours_model.datetime')
    def test_both_empty_string(self, datetime_mock):
        set_date(datetime_mock)
        self.assertRaises(AssertionError, self.obtain_hours_key_value, '', '')

    @patch('hours_model.datetime')
    def test_case_insensitive_acronyms(self, datetime_mock):
        set_date(datetime_mock)
        expected = ('F', [7, 0, 22, 0])
        self.assertEqual(self.obtain_hours_key_value('sTEast', 'friDAY'), expected)

    @patch('hours_model.datetime')
    def test_whitespace_around_location(self, datetime_mock):
        set_date(datetime_mock)
        expected = ('F', [7, 0, 22, 0])
        self.assertEqual(self.obtain_hours_key_value('  sTEast  ', 'friDAY'), expected)

    @patch('hours_model.datetime')
    def test_whitespace_around_day(self, datetime_mock):
        set_date(datetime_mock)
        expected = ('F', [7, 0, 22, 0])
        self.assertEqual(self.obtain_hours_key_value('STEAST', '  FRIDAY  '), expected)

    @patch('hours_model.datetime')
    def test_whitespace_between_location(self, datetime_mock):
        set_date(datetime_mock)
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'S TE A ST', 'FRIDAY')

    @patch('hours_model.datetime')
    def test_whitespace_between_day(self, datetime_mock):
        set_date(datetime_mock)
        self.assertRaises(AssertionError, self.obtain_hours_key_value, 'STEAST', 'F R ID AY')

    @patch('hours_model.datetime')
    def test_closed_location(self, datetime_mock):
        set_date(datetime_mock)
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

    @patch('hours_model.datetime')
    def test_location_day_all_caps(self, datetime_mock):
        set_date(datetime_mock)
        location = "STETSON WEST"
        day = "MONDAY"
        expected = "STETSON WEST is open from 11:00 AM - 8:00 PM on MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_acronym_day_all_caps(self, datetime_mock):
        set_date(datetime_mock)
        location = "STWEST"
        day = "MONDAY"
        expected = "STWEST is open from 11:00 AM - 8:00 PM on MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_day_mixed_case(self, datetime_mock):
        set_date(datetime_mock)
        location = "sTwEsT"
        day = "MonDaY"
        expected = "STWEST is open from 11:00 AM - 8:00 PM on MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_with_apostrophe_mixed_case(self, datetime_mock):
        set_date(datetime_mock)
        location = "cappy's"
        day = "tuesday"
        expected = "CAPPY'S is open from 6:30 AM - 2:00 AM on MONDAY-SUNDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_closed_on_day(self, datetime_mock):
        set_date(datetime_mock)
        location = "stwest"
        day = "SATURDAY"
        expected = "STWEST is CLOSED SATURDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)


class TestGetYesterday(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()
        self.get_yesterday = self.model._HoursModel__get_yesterday

    def test_sunday(self):
        self.assertEqual(self.get_yesterday('SUNDAY'), 'SATURDAY')
    
    def test_saturday(self):
        self.assertEqual(self.get_yesterday('SATURDAY'), 'FRIDAY')

    def test_monday(self):
        self.assertEqual(self.get_yesterday('MONDAY'), 'SUNDAY')
    
    def test_invalid_day(self):
        self.assertRaises(AssertionError, self.get_yesterday, 'TEST')
    
    def test_invalid_day_acronym(self):
        #TODO: This may not be invalid in the future
        self.assertRaises(AssertionError, self.get_yesterday, 'MON')


class TestConvertToDatetime(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()
        self.convert_to_datetime = self.model._HoursModel__convert_to_datetime

    @patch('hours_model.datetime')
    def test_same_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        self.assertEqual(self.convert_to_datetime(20, 30, 'SATURDAY'), datetime(2019, 11, 23, 20, 30))
    
    @patch('hours_model.datetime')
    def test_yesterday_normal_range(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        self.assertEqual(self.convert_to_datetime(20, 30, 'FRIDAY'), datetime(2019, 11, 22, 20, 30))
    
    @patch('hours_model.datetime')
    def test_yesterday_next_day_range(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        self.assertEqual(self.convert_to_datetime(25, 30, 'FRIDAY'), datetime(2019, 11, 23, 1, 30))
    
    @patch('hours_model.datetime')
    def test_two_days_behind_normal_range(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        self.assertEqual(self.convert_to_datetime(20, 30, 'THURSDAY'), datetime(2019, 11, 28, 20, 30))
    
    @patch('hours_model.datetime')
    def test_yesterday_normal_range_index_0_today(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertEqual(self.convert_to_datetime(20, 30, 'SATURDAY'), datetime(2019, 11, 23, 20, 30))

    @patch('hours_model.datetime')
    def test_yesterday_next_day_range_index_0_today(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertEqual(self.convert_to_datetime(25, 30, 'SATURDAY'), datetime(2019, 11, 24, 1, 30))
    
    @patch('hours_model.datetime')
    def test_negative_hours(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertRaises(AssertionError, self.convert_to_datetime, -1, 30, 'SATURDAY')
    
    @patch('hours_model.datetime')
    def test_negative_minutes(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertRaises(AssertionError, self.convert_to_datetime, 1, -1, 'SATURDAY')
    
    @patch('hours_model.datetime')
    def test_0_minutes(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertEqual(self.convert_to_datetime(25, 0, 'SATURDAY'), datetime(2019, 11, 24, 1, 0))
    
    @patch('hours_model.datetime')
    def test_60_minutes(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertRaises(AssertionError, self.convert_to_datetime, 1, 60, 'SATURDAY')

    @patch('hours_model.datetime')
    def test_greater_than_60_minutes(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertRaises(AssertionError, self.convert_to_datetime, 1, 61, 'SATURDAY')
    
    @patch('hours_model.datetime')
    def test_invalid_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        # TODO: This may not be an invalid day in the future
        self.assertRaises(AssertionError, self.convert_to_datetime, 1, 30, 'SAT')


class TestIsOpen(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    # it will always say not open if the given day is not the same day
    @patch('hours_model.datetime')
    def test_location_is_not_current_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        location = "STETSON WEST"
        day = "MONDAY"
        self.assertFalse(self.model.is_open(location, day))

    @patch('hours_model.datetime')
    def test_location_closed_entire_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertFalse(self.model.is_open(location, day))

    @patch('hours_model.datetime')
    def test_location_open_on_day_at_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertTrue(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_not_yet_open(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 3:59pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 59))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_past_closing_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:01pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 20, 1))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_at_closing_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 8:00pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 20, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_open_current_day_with_data_from_yesterday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 12:30am (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26, 0, 30))
        location = "OUTTAKES"
        day = "TUESDAY"
        self.assertTrue(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_closed_current_day_yesterday_data_closed(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 9:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 21, 30))
        location = "OUTTAKES"
        day = "SUNDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_closed_current_day_open_yesterday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 11:30am (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 11, 30))
        location = "OUTTAKES"
        day = "SATURDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_closed_current_day_yesterday_closed_full_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 25, 2019 10:30am (Monday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 25, 10, 30))
        location = "OUTTAKES"
        day = "MONDAY"
        self.assertFalse(self.model.is_open(location, day))


class TestTimeTillOpen(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_location_open_in_half_hour(self, datetime_mock):
        # Mock Date: Nov 24, 2019 3:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        datetime_mock.strptime = datetime.strptime
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 30)

    @patch('hours_model.datetime')
    def test_location_closed_entire_day(self, datetime_mock):
        # Mock Date: Nov 23, 2019 3:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 15, 30))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        datetime_mock.strptime = datetime.strptime
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
        datetime_mock.strptime = datetime.strptime
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), -1)

class TestGetLink(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_get_link_full_name(self, datetime_mock):
        datetime_mock.now = Mock(return_value=datetime(2019, 1, 1))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        datetime_mock.strptime = datetime.strptime
        link = "https://nudining.com/hours"
        self.assertEqual(link, self.model.get_link('stetson west'))

    @patch('hours_model.datetime')
    def test_get_link_alias(self, datetime_mock):
        datetime_mock.now = Mock(return_value=datetime(2019, 1, 1))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        datetime_mock.strptime = datetime.strptime
        link = "https://nudining.com/hours"
        self.assertEqual(link, self.model.get_link('stwest'))

    @patch('hours_model.datetime')
    def test_get_non_northeastern_location(self, datetime_mock):
        datetime_mock.now = Mock(return_value=datetime(2019, 1, 1))
        datetime_mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        datetime_mock.strptime = datetime.strptime
        link = "http://www.bostonshawarma.net"
        self.assertEqual(link, self.model.get_link('boston shawarma'))

class TestClosedAllDay(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_is_closed_all_day(self, datetime_mock):
        set_date(datetime_mock)
        self.assertTrue(self.model.closed_all_day('stwest', 'saturday'))
    
    @patch('hours_model.datetime')
    def test_is_not_closed_all_day(self, datetime_mock):
        set_date(datetime_mock)
        self.assertFalse(self.model.closed_all_day('stwest', 'sunday'))
    
    @patch('hours_model.datetime')
    def test_location_closed_now_but_not_whole_day(self, datetime_mock):
        set_date(datetime_mock)
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertFalse(self.model.closed_all_day(location, day))


if __name__ == '__main__':
    unittest.main()
