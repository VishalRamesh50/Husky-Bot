from discord.ext import commands

from .course_cleanup import CourseCleanup
from .course_embed import CourseEmbed
from .course_selection import CourseSelection
from .create_course import CreateCourse


def setup(client: commands.Bot):
    client.add_cog(CourseCleanup(client))
    client.add_cog(CourseEmbed(client))
    client.add_cog(CourseSelection(client))
    client.add_cog(CreateCourse(client))
