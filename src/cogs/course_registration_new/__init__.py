from discord.ext import commands

from .course_cleanup import CourseCleanupChannel
from .course_selection import CourseSelectionChannel
from .create_course import CreateCourseChannel


def setup(client: commands.Bot):
    client.add_cog(CourseCleanupChannel(client))
    client.add_cog(CourseSelectionChannel(client))
    client.add_cog(CreateCourseChannel(client))
