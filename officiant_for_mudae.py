from constants import Command, ButtonAction
from discord_elements import Account, Server, ServerOptions, AccountOptions

firefox_profile_dir = r"C:/Users/YourName/AppData/Roaming/Mozilla/Firefox/Profiles"

GOOD_REACTS = [
    ButtonAction.PURPLE,
    ButtonAction.YELLOW,
    ButtonAction.ORANGE,
    ButtonAction.RED,
    ButtonAction.RAINBOW,
    ButtonAction.LIGHT,
]

custom_account_options = AccountOptions(
    roll_order=[Command.ROLL_WAIFU_ANIMANGA, Command.ROLL_ANY],
    allowed_kakera_reacts=GOOD_REACTS,
)

users = [
    Account(
        "username1",
        f"{firefox_profile_dir}/vabnsd4f.DiscordUsername1",
        custom_account_options,
    ),
    Account(
        "username2",
        f"{firefox_profile_dir}/a2pgf8ar.DiscordUsername2",
    ),
]

servers = [
    Server(
        name="server 1",
        server_id=1111111111111111,
        roll_channel_id=1111111111111111,
        accounts=users,
    ),
    Server(
        name="server 2",
        server_id=222222222222,
        roll_channel_id=222222222222,
        accounts=users,
    ),
    Server(
        name="server 3",
        server_id=3333333,
        roll_channel_id=33333333,
        accounts=users,
        options=ServerOptions(do_daily_kakera=False, do_pokeslot=False),
    ),
]

if __name__ == "__main__":
    for server in servers:
        server.do_rolls()
