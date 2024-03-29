import os


# --------------- NU Channel IDs --------------------
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 485269858557100034))
BOT_SPAM_CHANNEL_ID = int(os.getenv("BOT_SPAM_CHANNEL_ID", 531665740521144341))
COURSE_REGISTRATION_CHANNEL_ID = int(
    os.getenv("COURSE_REGISTRATION_CHANNEL_ID", 485279507582943262)
)
NOT_REGISTERED_CHANNEL_ID = int(
    os.getenv("NOT_REGISTERED_CHANNEL_ID", 501193530325205003)
)
ROLES_CHANNEL_ID = int(os.getenv("ROLES_CHANNEL_ID", 928710482456641546))
WELCOME_CHANNEL_ID = int(os.getenv("WELCOME_CHANNEL_ID", 557325274534903815))
# --------------- Test Channel IDs -----------------
ERROR_LOG_CHANNEL_ID = int(os.getenv("ERROR_LOG_CHANNEL_ID", 685752035806806047))
