import re

# This checks that an input exactly matches the course format.
IS_COURSE_ACRONYM = re.compile(r"^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}$")
# This checks that a channel is a course channel by making sure it starts with something
# following the IS_COURSE_ACRONYM pattern. Doesn't exactly matter what comes after.
IS_COURSE = re.compile(r"^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2}")
# This should match all course channel topics. Starts with a IS_COURSE pattern
# and has additional information about how many students are enrolled.
IS_COURSE_TOPIC = re.compile(r"^[A-Z]{2}([A-Z]{2})?-\d{2}[\dA-Z]{2} \(\d+ enrolled\)$")
