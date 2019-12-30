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
        self.assertEqual(self.model.todays_locations, nu_dining.WINTER_INTERSESSION1)
        self.assertEqual(self.model.current_date_range, '12/14/19-12/20/19')
        self.assertEqual(self.model.date_name, ' **(Winter Intersession 1: Dec 14-20,2019)**')
    
    # test that when setting todays_location during a special event on the last
    # day it occurs, it will still change since the date is time agnostic
    @patch('hours_model.datetime')
    def test_set_todays_location_during_special_range_end_date_midday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 20, 2019 3:30pm (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 20, 15, 30))
        self.set_todays_location()
        # make sure that todays_locations are not equal to NORMAL LOCATIONS
        self.assertNotEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)
        # make sure that it has been set to WINTER INTERSESSION 1 Hours
        self.assertEqual(self.model.todays_locations, nu_dining.WINTER_INTERSESSION1)
        self.assertEqual(self.model.current_date_range, '12/14/19-12/20/19')
        self.assertEqual(self.model.date_name, ' **(Winter Intersession 1: Dec 14-20,2019)**')
    
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
        self.assertIsNone(self.model.current_date_range)
        self.assertEqual(self.model.date_name, '')
    
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
        self.assertEqual(self.model.todays_locations, nu_dining.WINTER_INTERSESSION1)
        self.assertEqual(self.model.current_date_range, '12/14/19-12/20/19')
        self.assertEqual(self.model.date_name, ' **(Winter Intersession 1: Dec 14-20,2019)**')
        # Mock Date: Nov 24, 2019 3:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 30))
        self.set_todays_location()
        # make sure that todays_locations are equal to NORMAL LOCATIONS
        self.assertEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)
        self.assertIsNone(self.model.current_date_range)
        self.assertEqual(self.model.date_name, '')
    
    @patch('hours_model.datetime')
    def test_passing_in_date_different_than_now(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 20, 2019 3:30pm (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 20, 15, 30))
        self.set_todays_location(datetime(2019, 12, 22))
        # make sure that todays_locations are not equal to NORMAL LOCATIONS/WINTER INTERSESSION 1 Hours
        self.assertNotEqual(self.model.todays_locations, nu_dining.NORMAL_LOCATIONS)
        self.assertNotEqual(self.model.todays_locations, nu_dining.WINTER_INTERSESSION1)
        # make sure that it has been set to WINTER INTERSESSION 2 Hours
        self.assertEqual(self.model.todays_locations, nu_dining.WINTER_INTERSESSION2)
        self.assertEqual(self.model.current_date_range, '12/21/19-12/27/19')
        self.assertEqual(self.model.date_name, ' **(Winter Intersession 2: Dec 21-27,2019)**')


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
    
    @patch('hours_model.datetime')
    def test_sample_data(self, datetime_mock):
        set_date(datetime_mock)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 1))
        self.assertTrue(self.model.valid_location("stwest"))
        # make sure that the current location is not STWEST from NORMAL_LOCATIONS
        self.assertNotEqual(self.model.current_location, nu_dining.STWEST)
        # make sure that the current location is the special STWEST_TEST value
        self.assertEqual(self.model.current_location, nu_dining.STWEST_TEST1)
        self.assertEqual(self.model.current_date_range, '1/1/18-1/3/18')
        self.assertEqual(self.model.date_name, ' **(Test Locations 1: Jan 1-3,2018)**')
    
    @patch('hours_model.datetime')
    def test_which_variables_are_set_when_false(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 1, 2018 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 1))
        self.assertFalse(self.model.valid_location("invalid location name"))
        # make sure that the current location has not been set
        self.assertIsNone(self.model.current_location)
        # however, the other variables have been set
        self.assertEqual(self.model.current_date_range, '1/1/18-1/3/18')
        self.assertEqual(self.model.date_name, ' **(Test Locations 1: Jan 1-3,2018)**')
    
    @patch('hours_model.datetime')
    def test_variables_reset_after_false(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 1, 2018 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 1))
        # valid location
        self.assertTrue(self.model.valid_location("stwest"))
        self.assertEqual(self.model.current_location, nu_dining.STWEST_TEST1)
        self.assertEqual(self.model.current_date_range, '1/1/18-1/3/18')
        self.assertEqual(self.model.date_name, ' **(Test Locations 1: Jan 1-3,2018)**')
        # invalid location
        self.assertFalse(self.model.valid_location("invalid location"))
        self.assertIsNone(self.model.current_location)
        self.assertEqual(self.model.current_date_range, '1/1/18-1/3/18')
        self.assertEqual(self.model.date_name, ' **(Test Locations 1: Jan 1-3,2018)**')
    
    @patch('hours_model.datetime')
    def test_datetime_given(self, datetime_mock):
        set_date(datetime_mock)
        # valid location using normal datetime
        self.assertTrue(self.model.valid_location("stwest"))
        self.assertEqual(self.model.current_location, nu_dining.STWEST)
        self.assertIsNone(self.model.current_date_range)
        self.assertEqual(self.model.date_name, '')
        # valid location with special datetime given
        self.assertTrue(self.model.valid_location("stwest", datetime(2018, 1, 1)))
        self.assertEqual(self.model.current_location, nu_dining.STWEST_TEST1)
        self.assertEqual(self.model.current_date_range, '1/1/18-1/3/18')
        self.assertEqual(self.model.date_name, ' **(Test Locations 1: Jan 1-3,2018)**')


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

    # test that day acronyms is valid
    def test_valid_day_acronym(self):
        self.assertTrue(self.model.valid_day("sat"))
    
    def test_valid_one_letter_day_acronym(self):
        self.assertTrue(self.model.valid_day("s"))
    
    def test_more_valid_acronyms(self):
        self.assertTrue(self.model.valid_day("th"))
    
    def test_tomorrow_valid(self):
        self.assertTrue(self.model.valid_day("tomorrow"))

    # test that an invalid day is not recognized
    def test_invalid_day(self):
        self.assertFalse(self.model.valid_day("munday"))


class TestGetTomorrow(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()
        self.get_tomorrow = self.model._HoursModel__get_tomorrow

    def test_sunday(self):
        self.assertEqual(self.get_tomorrow('SUNDAY'), 'MONDAY')
    
    def test_saturday(self):
        self.assertEqual(self.get_tomorrow('SATURDAY'), 'SUNDAY')

    def test_monday(self):
        self.assertEqual(self.get_tomorrow('MONDAY'), 'TUESDAY')

    def test_valid_three_letter_acronyms(self):
        self.assertEqual(self.get_tomorrow('MON'), 'TUESDAY')
    
    def test_valid_two_letter_acronyms(self):
        self.assertEqual(self.get_tomorrow('TU'), 'WEDNESDAY')
    
    def test_valid_one_letter_acronyms(self):
        self.assertEqual(self.get_tomorrow('F'), 'SATURDAY')
    
    def test_invalid_day(self):
        self.assertRaises(AssertionError, self.get_tomorrow, 'TEST')


class TestGetFullDay(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()
        self.get_full_day = self.model._HoursModel__get_full_day

    def test_fullday_given(self):
        self.assertEqual(self.get_full_day('SUNDAY'), 'SUNDAY')
    
    def test_three_letter_acronym(self):
        self.assertEqual(self.get_full_day('SAT'), 'SATURDAY')

    def test_one_letter_acronym(self):
        self.assertEqual(self.get_full_day('M'), 'MONDAY')
    
    def test_two_letter_acronym(self):
        self.assertEqual(self.get_full_day('TH'), 'THURSDAY')
    
    def test_invalid_day(self):
        self.assertRaises(AssertionError, self.get_full_day, 'TEST')
    
    @patch('hours_model.datetime')
    def test_tomorrow(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: November 23, 2019 (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23))
        self.assertEqual(self.get_full_day('TOMORROW'), 'SUNDAY')

class TestGetDatetimeRange(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.get_datetime_range = self.model._HoursModel__get_datetime_range

    def test_jan1_to_jan20(self):
        date_range: str = '01/01/19-01/20/19'
        start_datetime, end_datetime = self.get_datetime_range(date_range)
        self.assertEqual(start_datetime, datetime(2019, 1, 1))
        self.assertEqual(end_datetime, datetime(2019, 1, 20))
    
    def test_jan1_to_jan20_single_digit_month_and_days(self):
        date_range: str = '1/1/19-1/20/19'
        start_datetime, end_datetime = self.get_datetime_range(date_range)
        self.assertEqual(start_datetime, datetime(2019, 1, 1))
        self.assertEqual(end_datetime, datetime(2019, 1, 20))
    
    def test_month_out_of_range(self):
        date_range: str = '13/01/19-01/20/19'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_day_out_of_range(self):
        date_range: str = '11/40/19-01/20/19'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_day_out_of_range_for_month(self):
        date_range: str = '11/31/19-01/20/19'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_day_out_of_range_for_february(self):
        date_range: str = '2/29/19-01/20/19'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_yy_mm_dd_format(self):
        date_range: str = '19/2/19-19/2/25'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_mm_dd_yyyy_format(self):
        date_range: str = '12/2/2019-12/6/2019'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_missing_end_date(self):
        date_range: str = '19/2/19-'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_no_hyphen(self):
        date_range: str = '1/1/19 1/20/19'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)
    
    def test_space_around_hyphen(self):
        date_range: str = '1/1/19 - 1/20/19'
        self.assertRaises(AssertionError, self.get_datetime_range, date_range)


class TestGetNumDaysInRange(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.get_num_days_in_range = self.model._HoursModel__get_num_days_in_range

    @patch('hours_model.datetime')
    def test_normal_range(self, datetime_mock):
        set_date(datetime_mock)
        self.assertEqual(self.get_num_days_in_range('MONDAY'), -1)

    @patch('hours_model.datetime')
    def test_not_in_range(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 1, 2018 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 1))
        self.assertEqual(self.get_num_days_in_range('THURSDAY'), 0)

    @patch('hours_model.datetime')
    def test_WINTER_INTERSESSION1_monday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 19, 2019 (Thursday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 19))
        self.assertEqual(self.get_num_days_in_range('MONDAY'), 1)
    
    @patch('hours_model.datetime')
    def test_spring_break_friday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 5, 2019 (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 5))
        self.assertEqual(self.get_num_days_in_range('FRIDAY'), 2)
    
    @patch('hours_model.datetime')
    def test_spring_break_friday_acronyms(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 5, 2019 (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 5))
        self.assertEqual(self.get_num_days_in_range('FRI'), 2)
    
    @patch('hours_model.datetime')
    def test_not_in_spring_break_given_date_is_spring_break(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Feb 28, 2019 (Thursday)
        datetime_mock.now = Mock(return_value=datetime(2019, 2, 28))
        self.assertEqual(self.get_num_days_in_range('FRIDAY', datetime(2019, 3, 1)), 2)
    
    @patch('hours_model.datetime')
    def test_invalid_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 5, 2019 (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 5))
        self.assertRaises(AssertionError, self.get_num_days_in_range, 'invalid')


class TestWhichDayNum(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.which_day_num = self.model._HoursModel__which_day_num

    @patch('hours_model.datetime')
    def test_spring_break_friday1(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 1, 2019 (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 1))
        self.assertEqual(self.which_day_num('FRIDAY'), 1)

    @patch('hours_model.datetime')
    def test_spring_break_friday2(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 3, 2019 (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 3))
        self.assertEqual(self.which_day_num('FRIDAY'), 2)
    
    @patch('hours_model.datetime')
    def test_spring_break_given_date_different_than_current(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 1, 2019 (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 1))
        self.assertEqual(self.which_day_num('FRIDAY', datetime(2019, 3, 3)), 2)
    
    @patch('hours_model.datetime')
    def test_normal_date_range(self, datetime_mock):
        set_date(datetime_mock)
        self.assertRaises(AssertionError, self.which_day_num, 'FRIDAY')


class TestObtainHoursKeyValue(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.obtain_hours_key_value = self.model._HoursModel__obtain_hours_key_value

    @patch('hours_model.datetime')
    def test_normal_full_day(self, datetime_mock):
        set_date(datetime_mock)
        expected = ('S', [-1, -1, -1, -1])
        self.assertEqual(self.obtain_hours_key_value('STWEST', 'SATURDAY'), expected)
    
    @patch('hours_model.datetime')
    def test_normal_three_letter_acronym(self, datetime_mock):
        set_date(datetime_mock)
        expected = ('S', [-1, -1, -1, -1])
        self.assertEqual(self.obtain_hours_key_value('STWEST', 'SAT'), expected)

    @patch('hours_model.datetime')
    def test_normal_one_letter_acronym(self, datetime_mock):
        set_date(datetime_mock)
        expected = ('S', [-1, -1, -1, -1])
        self.assertEqual(self.obtain_hours_key_value('STWEST', 'S'), expected)

    @patch('hours_model.datetime')
    def test_spring_break_friday_stwest(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 3, 2019 (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 3))
        expected = ('S1U1MTWRF2S2U2', [-1, -1, -1, -1])
        self.assertEqual(self.obtain_hours_key_value('STETSON WEST', 'FRIDAY'), expected)
    
    @patch('hours_model.datetime')
    def test_spring_break_saturday_steast(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 1, 2019 (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 1))
        expected = ('S1U1', [8, 00, 20, 00])
        self.assertEqual(self.obtain_hours_key_value('STEAST', 'SATURDAY'), expected)
    
    @patch('hours_model.datetime')
    def test_spring_break_saturday2_steast(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Mar 3, 2019 (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 3, 3))
        expected = ('S2', [8, 00, 20, 00])
        self.assertEqual(self.obtain_hours_key_value('STEAST', 'SATURDAY'), expected)
    
    @patch('hours_model.datetime')
    def test_current_date_normal_next_day_special(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Feb 28, 2019 (Thursday)
        datetime_mock.now = Mock(return_value=datetime(2019, 2, 28))
        expected = ('F1', [7, 00, 16, 00])
        # make sure it's not using normal hours and is instead
        # using special hours even though the current date is normal
        self.assertNotEqual(self.obtain_hours_key_value('IV', 'FRIDAY'), ('F', [7, 00, 21, 00]))
        self.assertEqual(self.obtain_hours_key_value('IV', 'FRIDAY'), expected)

    @patch('hours_model.datetime')
    def test_holiday1_to_holiday2(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 1, 2018 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 1))
        expected = ('R', [8, 0, 15, 0])
        self.assertEqual(self.obtain_hours_key_value('STETSON WEST', 'THURSDAY'), expected)
    
    @patch('hours_model.datetime')
    def test_holiday2_to_normal(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 7, 2018 (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 7))
        expected = ('MTWR', [11, 0, 20, 0])
        self.assertEqual(self.obtain_hours_key_value('STETSON WEST', 'MONDAY'), expected)

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


class TestObtainDayRange(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()
        self.obtain_day_range = self.model._HoursModel__obtain_day_range

    def test_single_day(self):
        self.assertEqual(self.obtain_day_range('T', 'TUESDAY'), 'TUESDAY')

    def test_two_days(self):
        self.assertEqual(self.obtain_day_range('TW', 'TUESDAY'), 'TUESDAY-WEDNESDAY')

    def test_day_range_acronym_not_first_letter_of_day(self):
        self.assertEqual(self.obtain_day_range('MTWR', 'TUESDAY'), 'MONDAY-THURSDAY')
    
    def test_everyday(self):
        self.assertEqual(self.obtain_day_range('MTWRFSU', 'TUESDAY'), 'EVERYDAY')
    
    def test_everyday_different_order(self):
        self.assertEqual(self.obtain_day_range('SUMTWRF', 'TUESDAY'), 'EVERYDAY')
    
    def test_everyday_fully_scrambled(self):
        self.assertEqual(self.obtain_day_range('WRTFSUM', 'TUESDAY'), 'EVERYDAY')
    
    def test_with_numbered_days_everyday(self):
        self.assertEqual(self.obtain_day_range('M1T1W1R1F1S1U1', 'TUESDAY'), 'EVERYDAY')
    
    def test_everyday_more_than_one_week(self):
        self.assertEqual(self.obtain_day_range('MTWRFSUMT', 'TUESDAY'), 'EVERYDAY')

    def test_weekday(self):
        self.assertEqual(self.obtain_day_range('MTWRF', 'TUESDAY'), 'WEEKDAYS')
    
    def test_weekday_with_saturday(self):
        self.assertEqual(self.obtain_day_range('MTWRFS', 'TUESDAY'), 'MONDAY-SATURDAY')
    
    def test_weekend(self):
        self.assertEqual(self.obtain_day_range('SU', 'SATURDAY'), 'WEEKENDS')

    def test_with_numbered_days_weekend(self):
        self.assertEqual(self.obtain_day_range('S1U1', 'SATURDAY'), 'WEEKENDS')
    
    def test_FSU_range_searching_saturday(self):
        self.assertEqual(self.obtain_day_range('FSU', 'SATURDAY'), 'FRIDAY-SUNDAY')
    
    def test_FSU_range_searching_friday(self):
        self.assertEqual(self.obtain_day_range('FSU', 'FRIDAY'), 'FRIDAY-SUNDAY')
    
    def test_day_acronyms_work(self):
        self.assertEqual(self.obtain_day_range('FSU', 'fri'), 'FRIDAY-SUNDAY')
    
    def test_weekdays(self):
        self.assertEqual(self.obtain_day_range('MTWRF', 'TUESDAY'), 'WEEKDAYS')
    
    def test_weekdays_not_in_order(self):
        self.assertEqual(self.obtain_day_range('WRFMT', 'TUESDAY'), 'WEEKDAYS')
    
    def test_day_not_in_range(self):
        self.assertRaises(AssertionError, self.obtain_day_range, 'SU', 'TUESDAY')

    def test_with_numbered_days_weekdays(self):
        self.assertEqual(self.obtain_day_range('M1T1W1R1F1', 'TUESDAY'), 'WEEKDAYS')

    def test_whitespace_between_days(self):
        self.assertEqual(self.obtain_day_range('U   W', 'SUNDAY'), 'SUNDAY-WEDNESDAY')

    def test_whitespace_around_days(self):
        self.assertEqual(self.obtain_day_range('  UW  ', 'SUNDAY'), 'SUNDAY-WEDNESDAY')

    def test_whitespace_around_and_between_days(self):
        self.assertEqual(self.obtain_day_range('  U   W  ', 'SUNDAY'), 'SUNDAY-WEDNESDAY')
    
    def test_day_empty_string(self):
        self.assertRaises(AssertionError, self.obtain_day_range, '', 'TUESDAY')
    
    def test_invalid_day(self):
        self.assertRaises(AssertionError, self.obtain_day_range, 'FSU', 'test')


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


class TestLocationHoursMsg(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_location_day_all_caps(self, datetime_mock):
        set_date(datetime_mock)
        location = "STETSON WEST"
        day = "MONDAY"
        expected = "STETSON WEST is open from 11:00 AM - 8:00 PM MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_acronym_day_all_caps(self, datetime_mock):
        set_date(datetime_mock)
        location = "STWEST"
        day = "MONDAY"
        expected = "STWEST is open from 11:00 AM - 8:00 PM MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_day_mixed_case(self, datetime_mock):
        set_date(datetime_mock)
        location = "sTwEsT"
        day = "MonDaY"
        expected = "STWEST is open from 11:00 AM - 8:00 PM MONDAY-THURSDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_with_apostrophe_mixed_case(self, datetime_mock):
        set_date(datetime_mock)
        location = "cappy's"
        day = "tuesday"
        expected = "CAPPY'S is open from 6:30 AM - 2:00 AM EVERYDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_location_closed_on_day(self, datetime_mock):
        set_date(datetime_mock)
        location = "stwest"
        day = "SATURDAY"
        expected = "STWEST is CLOSED SATURDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_open_weekdays(self, datetime_mock):
        set_date(datetime_mock)
        location = "popeyes"
        day = "TUESDAY"
        expected = "POPEYES is open from 10:30 AM - 9:00 PM WEEKDAYS"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_open_weekends(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: December 15, 2019 (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 15))
        location = "STEAST"
        day = "saturday"
        expected = "STEAST is open from 8:00 AM - 7:00 PM WEEKENDS **(Winter Intersession 2: Dec 21-27,2019)**"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_stwest_closed_holiday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: December 22, 2019 11:18pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 22, 23, 18))
        location = "stwest"
        day = "sunday"
        expected = "STWEST is CLOSED EVERYDAY **(Winter Intersession 2: Dec 21-27,2019)**"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_0am_converts_to_12am(self, datetime_mock):
        set_date(datetime_mock)
        location = "wings"
        day = "sunday"
        expected = "WINGS is open from 11:00 AM - 12:00 AM SUNDAY"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)

    @patch('hours_model.datetime')
    def test_holiday_different_years(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: December 28, 2019 (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 28))
        location = "stwest"
        day = "sunday"
        expected = "STWEST is CLOSED EVERYDAY **(Winter Intersession 3: Dec 28,2019-Jan 5,2020)**"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_non_holiday_item_during_holiday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: December 23, 2019 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 23))
        location = "resmail"
        day = "sunday"
        expected = "RESMAIL is CLOSED SUNDAY **(Winter Intersession 3: Dec 28,2019-Jan 5,2020)**"
        self.assertEqual(self.model.location_hours_msg(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_wendys_open(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 29, 2019 6:45pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 29, 18, 45))
        location = "WENDYS"
        day = "SUNDAY"
        location_msg = "WENDYS is open from 9:00 AM - 12:00 AM THURSDAY-TUESDAY *(Normal Hours: Not guaranteed to be correct during special hours)*"
        self.assertEqual(self.model.location_hours_msg(location, day), location_msg)
    
    @patch('hours_model.datetime')
    def test_wendys_closed(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 25, 2019 6:45pm (Wednesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 25, 18, 45))
        location = "WENDYS"
        day = "WEDNESDAY"
        location_msg = "WENDYS is CLOSED WEDNESDAY *(Normal Hours: Not guaranteed to be correct during special hours)*"
        self.assertEqual(self.model.location_hours_msg(location, day), location_msg)


class TestGetHoursOfOperation(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_closed(self, datetime_mock):
        set_date(datetime_mock)
        location = "STETSON WEST"
        day = "SATURDAY"
        expected = "CLOSED"
        self.assertEqual(self.model.get_hours_of_operation(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_open_single_hour(self, datetime_mock):
        set_date(datetime_mock)
        location = "STETSON WEST"
        day = "SUNDAY"
        expected = "4:00 PM - 8:00 PM"
        self.assertEqual(self.model.get_hours_of_operation(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_open_double_hour(self, datetime_mock):
        set_date(datetime_mock)
        location = "STETSON WEST"
        day = "FRIDAY"
        expected = "11:00 AM - 5:00 PM"
        self.assertEqual(self.model.get_hours_of_operation(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_double_closing_hour(self, datetime_mock):
        set_date(datetime_mock)
        location = "STEAST"
        day = "FRIDAY"
        expected = "7:00 AM - 10:00 PM"
        self.assertEqual(self.model.get_hours_of_operation(location, day), expected)
    
    @patch('hours_model.datetime')
    def test_normal_location_during_holiday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 24, 2019 (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 24))
        location = "wings"
        day = "tuesday"
        expected = "4:00 PM - 12:00 AM"
        self.assertEqual(self.model.get_hours_of_operation(location, day), expected)

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
    
    def test_valid_day_acronym(self):
        self.assertEqual(self.get_yesterday('MON'), 'SUNDAY')


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
    def test_valid_day_acronym(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        self.assertEqual(self.convert_to_datetime(1, 30, 'SAT'), datetime(2019, 11, 23, 1, 30))

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


class TestIsOpen(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    # it will always say not open if the given day is not the same day
    @patch('hours_model.datetime')
    def test_is_not_current_day(self, datetime_mock):
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
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_closed_entire_given_day_open_current_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_closed_entire_current_day_open_given_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 4:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 16, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
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
    def test_location_at_opening_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:00pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertTrue(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_open_current_day_with_data_from_yesterday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 12:30am (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26, 0, 30))
        location = "OUTTAKES"
        day = "TUESDAY"
        self.assertTrue(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_location_closed_entire_current_day_would_be_open_yesterday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 2:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 14, 00))
        location = "OUTTAKES"
        day = "SUNDAY"
        self.assertFalse(self.model.is_open(location, day))

    @patch('hours_model.datetime')
    def test_location_closed_entire_current_day_yesterday_data_closed(self, datetime_mock):
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
    
    @patch('hours_model.datetime')
    def test_looking_yesterday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 22, 2019 11:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 22, 23, 30))
        location = "STEAST"
        day = "SUNDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_non_holiday_location(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 23, 2019 11:30am (Monday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 23, 11, 30))
        location = "RESMAIL"
        day = "MONDAY"
        self.assertTrue(self.model.is_open(location, day))
        self.assertEqual(self.model.date_name, ' **(Winter Intersession 2: Dec 21-27,2019)**')
    
    @patch('hours_model.datetime')
    def test_wendys(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 29, 2019 6:45pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 29, 18, 45))
        location = "WENDYS"
        day = "SUNDAY"
        self.assertTrue(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_wendys_closed(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 25, 2019 6:45pm (Wednesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 25, 18, 45))
        location = "WENDYS"
        day = "WEDNESDAY"
        self.assertFalse(self.model.is_open(location, day))
    
    @patch('hours_model.datetime')
    def test_resmail_sunday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Dec 23, 2019 11:30am (Monday)
        datetime_mock.now = Mock(return_value=datetime(2019, 12, 23, 11, 30))
        location = "RESMAIL"
        day = "SUNDAY"
        self.assertFalse(self.model.is_open(location, day))


class TestTimeTillOpen(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_location_open_in_half_hour(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 3:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 30)
        self.assertNotEqual(str(self.model.time_till_open(location, day)), '30.0')
        self.assertEqual(str(self.model.time_till_open(location, day)), '30')

    @patch('hours_model.datetime')
    def test_current_location_closed_entire_day_given_location_not(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 3:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 15, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
        # should not be 30 mins till open since it won't be open until the next day
        self.assertNotEqual(self.model.time_till_open(location, day), 30)
        # should be equal to 24 hours + 30 mins to be opening at 4:30pm on Sunday
        self.assertEqual(self.model.time_till_open(location, day), 1470)
    
    @patch('hours_model.datetime')
    def test_two_days_apart(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 3:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 15, 30))
        location = "STETSON WEST"
        day = "MONDAY"
        # should be equal to 24 hours + 19hrs 30mins to be opening at 11:00am on Monday
        self.assertEqual(self.model.time_till_open(location, day), 2610)
    
    @patch('hours_model.datetime')
    def test_given_and_current_location_closed_entire_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 3:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 15, 30))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertEqual(self.model.time_till_open(location, day), -1)
    
    @patch('hours_model.datetime')
    def test_given_location_closed_entire_day_current_location_not(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 3:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 30))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertEqual(self.model.time_till_open(location, day), -1)
    
    @patch('hours_model.datetime')
    def test_right_before_location_opening(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 3:59pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 59))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 1)

    @patch('hours_model.datetime')
    def test_location_at_opening_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:00pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 0)
    
    @patch('hours_model.datetime')
    def test_location_already_open(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 0)
    
    @patch('hours_model.datetime')
    def test_location_right_before_closing_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 7:59pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 19, 59))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 0)

    @patch('hours_model.datetime')
    def test_location_at_closing_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 8:00pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 20, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 0)
    
    @patch('hours_model.datetime')
    def test_location_after_closing_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 9:00pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 21, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_open(location, day), 0)
    
    @patch('hours_model.datetime')
    def test_location_open_by_yesterday_data(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 12:30am (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26, 0, 30))
        location = "OUTTAKES"
        day = "TUESDAY"
        # should not equal 10hrs 30mins to open at 11am
        self.assertNotEqual(self.model.time_till_open(location, day), 630)
        # should equal 0 since it is still open according to yesterday's data
        self.assertEqual(self.model.time_till_open(location, day), 0)
    
    @patch('hours_model.datetime')
    def test_location_past_open_by_yesterday_data(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 1:00am (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26, 1, 00))
        location = "OUTTAKES"
        day = "TUESDAY"
        # should not equal 0 since it's not open even according to yesterday's data
        self.assertNotEqual(self.model.time_till_open(location, day), 0)
        # should equal 10hrs to open at 11am
        self.assertEqual(self.model.time_till_open(location, day), 600)


class TestTimeTillClosing(unittest.TestCase):

    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_location_closing_in_half_hour(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 7:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 19, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_closing(location, day), 30)
        self.assertNotEqual(str(self.model.time_till_closing(location, day)), '30.0')
        self.assertEqual(str(self.model.time_till_closing(location, day)), '30')

    @patch('hours_model.datetime')
    def test_current_location_closed_entire_day_given_location_not(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 7:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 19, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
        # should not be 30 mins till close since it won't be closing until the next day
        self.assertNotEqual(self.model.time_till_closing(location, day), 30)
        # should be equal to 24 hours + 30 mins to be closing at 8pm on Sunday
        self.assertEqual(self.model.time_till_closing(location, day), 1470)
    
    @patch('hours_model.datetime')
    def test_two_days_apart(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 7:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 19, 30))
        location = "STETSON WEST"
        day = "MONDAY"
        # should be equal to 48 hours + 30mins to be closing at 8pm on Monday
        self.assertEqual(self.model.time_till_closing(location, day), 2910)
    
    @patch('hours_model.datetime')
    def test_given_and_current_location_closed_entire_day(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 23, 2019 7:30pm (Saturday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 23, 19, 30))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertEqual(self.model.time_till_closing(location, day), -1)
    
    @patch('hours_model.datetime')
    def test_given_location_closed_entire_day_current_location_not(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 7:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 19, 30))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertEqual(self.model.time_till_closing(location, day), -1)
    
    @patch('hours_model.datetime')
    def test_right_before_location_opening(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 15, 59))
        location = "STETSON WEST"
        day = "SUNDAY"
        # equal to 4 hours + 1min to close at 8pm on Monday
        self.assertEqual(self.model.time_till_closing(location, day), 241)

    @patch('hours_model.datetime')
    def test_location_at_opening_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        # equal to 4 hours to close at 8pm on Monday
        self.assertEqual(self.model.time_till_closing(location, day), 240)
    
    @patch('hours_model.datetime')
    def test_location_already_open(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 16, 30))
        location = "STETSON WEST"
        day = "SUNDAY"
        # equal to 3hrs 30mins to close at 8pm on Monday
        self.assertEqual(self.model.time_till_closing(location, day), 210)
    
    @patch('hours_model.datetime')
    def test_location_right_before_closing_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 19, 59))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_closing(location, day), 1)

    @patch('hours_model.datetime')
    def test_location_at_closing_time(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 4:30pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 20, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_closing(location, day), 0)
    
    @patch('hours_model.datetime')
    def test_location_already_closed(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 9:00pm (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24, 21, 00))
        location = "STETSON WEST"
        day = "SUNDAY"
        self.assertEqual(self.model.time_till_closing(location, day), 0)
    
    @patch('hours_model.datetime')
    def test_location_open_by_yesterday_data(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 12:30am (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26, 0, 30))
        location = "OUTTAKES"
        day = "TUESDAY"
        # should not equal 24hrs 30mins to close at 1am
        self.assertNotEqual(self.model.time_till_closing(location, day), 1470)
        # should equal 0 since it is still open according to yesterday's data
        self.assertEqual(self.model.time_till_closing(location, day), 30)
    
    @patch('hours_model.datetime')
    def test_location_at_closing_time_by_yesterday_data(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 1:00am (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26, 1, 00))
        location = "OUTTAKES"
        day = "TUESDAY"
        # should not equal 0 since it's not open according to yesterday's data
        self.assertNotEqual(self.model.time_till_closing(location, day), 0)
        # should equal 24hrs to close at 1am
        self.assertEqual(self.model.time_till_closing(location, day), 1440)
    
    @patch('hours_model.datetime')
    def test_location_past_closing_time_by_yesterday_data(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 1:00am (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26, 1, 30))
        location = "OUTTAKES"
        day = "TUESDAY"
        # should not equal 0 since it's not open according to yesterday's data
        self.assertNotEqual(self.model.time_till_closing(location, day), 0)
        # should equal 24hrs to close at 1am
        self.assertEqual(self.model.time_till_closing(location, day), 1410)


class TestGetToday(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_sunday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 24, 2019 (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 24))
        self.assertEqual(self.model.get_today(), 'SUNDAY')
    
    @patch('hours_model.datetime')
    def test_monday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 25, 2019 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 25))
        self.assertEqual(self.model.get_today(), 'MONDAY')
    
    @patch('hours_model.datetime')
    def test_tuesday(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 26))
        self.assertEqual(self.model.get_today(), 'TUESDAY')
    
    @patch('hours_model.datetime')
    def test_switching_dates(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Nov 26, 2019 (Tuesday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 27))
        self.assertEqual(self.model.get_today(), 'WEDNESDAY')
        # Mock Date: Nov 28, 2019 (Friday)
        datetime_mock.now = Mock(return_value=datetime(2019, 11, 29))
        self.assertEqual(self.model.get_today(), 'FRIDAY')

class TestGetLink(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    @patch('hours_model.datetime')
    def test_get_link_full_name(self, datetime_mock):
        set_date(datetime_mock)
        link = "https://nudining.com/public/hours-of-operation"
        self.assertEqual(link, self.model.get_link('stetson west'))

    @patch('hours_model.datetime')
    def test_get_link_alias(self, datetime_mock):
        set_date(datetime_mock)
        link = "https://nudining.com/public/hours-of-operation"
        self.assertEqual(link, self.model.get_link('stwest'))

    @patch('hours_model.datetime')
    def test_get_non_northeastern_location(self, datetime_mock):
        set_date(datetime_mock)
        link = "http://www.bostonshawarma.net"
        self.assertEqual(link, self.model.get_link('boston shawarma'))
    
    @patch('hours_model.datetime')
    def test_get_special_link(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 1, 2018 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 1))
        link = "www.fakelink.com"
        self.assertEqual(link, self.model.get_link('stwest'))
    
    @patch('hours_model.datetime')
    def test_get_special_link_from_different_range_than_current_date(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 1, 2018 (Monday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 1))
        link = "www.differentfakelink.com"
        self.assertEqual(link, self.model.get_link('stwest', 'thursday'))
    
    @patch('hours_model.datetime')
    def test_get_link_special_to_normal(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 5, 2018 (Friday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 5))
        link = "https://nudining.com/public/hours-of-operation"
        self.assertEqual(link, self.model.get_link('stwest', 'thursday'))

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
    
    @patch('hours_model.datetime')
    def test_closed_next_range_not_now(self, datetime_mock):
        set_date(datetime_mock)
        # Mock Date: Jan 5, 2018 (Friday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 5))
        location = "STETSON WEST"
        day = "SATURDAY"
        self.assertFalse(self.model.closed_all_day(location, day))
        # Mock Date: Jan 7, 2018 (Sunday)
        datetime_mock.now = Mock(return_value=datetime(2018, 1, 7))
        self.assertTrue(self.model.closed_all_day(location, day))

class TestGetAvailableLocations(unittest.TestCase):
    def setUp(self):
        self.model = HoursModel()

    def test_is_alphabetical(self):
        result = self.model.get_available_locations()
        locations = result.replace('.', '').split(', ')
        locations = [i.upper() for i in locations]
        self.assertEqual(locations, sorted(locations))
    
    def test_is_up_to_date(self):
        result = self.model.get_available_locations()
        locations = result.replace('.', '').split(', ')
        locations = [i.upper() for i in locations]
        normal_locations = []
        for aliases in nu_dining.NORMAL_LOCATIONS:
            normal_locations.append(aliases[0])
        self.assertListEqual(locations, normal_locations)


if __name__ == '__main__':
    unittest.main()
