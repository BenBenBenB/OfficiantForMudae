from constants import Command, ButtonAction, Emoji
from discord_elements import Account, Server, ServerOptions, AccountOptions
from officiant_for_mudae import schedule_rolls_for_servers


GOOD_REACTS = [
    ButtonAction.PURPLE,
    ButtonAction.YELLOW,
    ButtonAction.ORANGE,
    ButtonAction.RED,
    ButtonAction.RAINBOW,
    ButtonAction.LIGHT,
]

with open(".\wishlist.txt") as f:
    wishlist = f.read().splitlines()
with open(".\wishlist_series.txt") as f:
    wishlist_series = f.read().splitlines()

custom_account_options = AccountOptions(
    roll_order=[Command.ROLL_WAIFU_ANIMANGA, Command.ROLL_ANY],
    allowed_kakera_reacts=GOOD_REACTS,
    react_emoji=Emoji.GAME_DIE,
    wishlist=wishlist,
    wishlist_series=wishlist_series,
    announcement_message=Command.QUOT_IMAGE,
)

main = Account(
    "mainusername",
    r"C:/Users/BenB/AppData/Roaming/Mozilla/Firefox/Profiles/blablabla1",
    custom_account_options,
)
alt = Account(
    "altusername",
    r"C:/Users/BenB/AppData/Roaming/Mozilla/Firefox/Profiles/blablabla2",
    custom_account_options,
)
users = [main, alt]

my_options = ServerOptions(announce_start=True)

servers = [
    Server(
        name="Dev",
        server_id=1111111111,
        roll_channel_id=11111111111,
        minute_of_hour_to_roll=24,
        accounts=users,
        options=my_options,
    ),
    Server(
        name="Another",
        server_id=2222222222,
        roll_channel_id=22222222222,
        minute_of_hour_to_roll=14,
        accounts=users,
        options=my_options,
    ),
    Server(
        name="Different Options and Accounts",
        server_id=333333333,
        roll_channel_id=33333333333,
        minute_of_hour_to_roll=51,
        accounts=[main],
        options=ServerOptions(
            do_daily_kakera=False, do_pokeslot=False, announce_start=True
        ),
    ),
]

if __name__ == "__main__":
    schedule_rolls_for_servers(servers)
