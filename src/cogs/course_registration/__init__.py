from discord.ext import commands

from .course_cleanup import CourseCleanup
from .course_content import CourseContent
from .course_selection import CourseSelection
from .create_course import CreateCourse


async def setup(client: commands.Bot):
    await client.add_cog(CourseCleanup(client))
    await client.add_cog(CourseContent(client))
    await client.add_cog(CourseSelection(client))
    await client.add_cog(CreateCourse(client))
