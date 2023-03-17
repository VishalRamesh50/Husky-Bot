import sys

sys.path.append("src")
import pytest  # noqa: E402
import discord  # noqa: E402
from cogs.activity import Activity  # noqa: E402
from discord.ext import commands  # noqa: E402

client = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@pytest.fixture()
def activity_match():
    return Activity(client)._Activity__activity_match


class TestActivityMatch:
    def test_exact_match(self, activity_match):
        assert activity_match("rocket league", "Rocket League")

    def test_partial_match(self, activity_match):
        assert activity_match("league", "Rocket League")

    def test_partial_match_other_possibility(self, activity_match):
        assert activity_match("league", "League of Legends")

    def test_acronym_match(self, activity_match):
        assert activity_match("rl", "Rocket League")

    def test_acronym_match_of(self, activity_match):
        assert activity_match("lol", "League of Legends")

    def test_not_full_acronym(self, activity_match):
        assert activity_match("sg", "Some Game Here")

    def test_with_colon(self, activity_match):
        assert activity_match("counter strike", "Counter-Strike: Global Offensive")

    def test_with_dash_in_search(self, activity_match):
        assert activity_match("counter-strike", "Counter-Strike: Global Offensive")

    def test_acronym_when_activity_has_special_chars(self, activity_match):
        assert activity_match("csgo", "Counter-Strike: Global Offensive")

    def test_special_char_both_acronym(self, activity_match):
        assert activity_match("cs:go", "Counter-Strike: Global Offensive")

    def test_vscode(self, activity_match):
        assert activity_match("vs code", "Visual Studio Code")

    def test_pubg(self, activity_match):
        assert activity_match("pubg", "PLAYERUKNOWNSBATTLEGROUNDS")

    def test_partial_acronym_with_special_chars(self, activity_match):
        assert activity_match("cod", "Call of Duty: Modern Warfare")
