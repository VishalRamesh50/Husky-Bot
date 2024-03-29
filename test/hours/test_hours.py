import sys
sys.path.append('src')
import discord  # noqa: E402
import unittest  # noqa: E402
from discord.ext import commands  # noqa: E402
from cogs.hours.hours import Hours  # noqa: E402

client = commands.Bot(command_prefix='.', intents=discord.Intents.all())


class TestParseComma(unittest.TestCase):

    def setUp(self):
        self.parse_comma = Hours(client)._Hours__parse_comma

    # when two arguments exist but neither word has a comma
    def test_parse_comma_no_comma_two_words(self):
        day, comma, content = self.parse_comma(("hello", "there"))
        self.assertEqual(day, '')
        self.assertEqual(comma, False)
        self.assertEqual(content, 'HELLO THERE')

    # when two arguments exist but one has a comma
    def test_parse_comma_with_comma_two_words(self):
        day, comma, content = self.parse_comma(("iv,", "monday"))
        self.assertEqual(day, 'MONDAY')
        self.assertEqual(comma, True)
        self.assertEqual(content, 'IV')

    # when one argument exists but has a comma with two distinct words
    def test_parse_comma_with_comma_one_word(self):
        day, comma, content = self.parse_comma(("iv,monday",))
        self.assertEqual(day, 'MONDAY')
        self.assertEqual(comma, True)
        self.assertEqual(content, 'IV')

    # when one argument exists with a comma and the second word has whitespace
    # surrounding it
    def test_parse_comma_with_comma_whitespace_before_and_after_word(self):
        day, comma, content = self.parse_comma(("iv,   monday     ",))
        self.assertEqual(day, 'MONDAY')
        self.assertEqual(comma, True)
        self.assertEqual(content, 'IV')

    # when one argument exists but the second words has whitespace both
    # before, after, and in-between the word
    def test_parse_comma_with_comma_whitespace_before_after_between_day(self):
        day, comma, content = self.parse_comma(("iv,   m o nd ay     ",))
        self.assertNotEqual(day, 'MONDAY')
        self.assertEqual(day, 'M O ND AY')
        self.assertEqual(comma, True)
        self.assertEqual(content, 'IV')

    # when one argument exists where the first word has whitespace before and after
    # and a comma exists
    def test_parse_comma_with_comma_whitespace_before_after_two_words_location(self):
        day, comma, content = self.parse_comma(("   stetson west   , monday",))
        self.assertEqual(day, 'MONDAY')
        self.assertEqual(comma, True)
        self.assertEqual(content, 'STETSON WEST')


if __name__ == '__main__':
    unittest.main()
