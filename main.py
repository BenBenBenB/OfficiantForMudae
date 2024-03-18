from constants import Command, ButtonAction, Emoji
from discord_elements import Account, Server, ServerOptions, AccountOptions
import logging
from tendo import singleton
from officiant_for_mudae import schedule_rolls_for_servers

GOOD_REACTS = [
    ButtonAction.PURPLE,
    ButtonAction.YELLOW,
    ButtonAction.ORANGE,
    ButtonAction.RED,
    ButtonAction.RAINBOW,
    ButtonAction.LIGHT,
]

with open(r".\wishlist.txt") as f:
    wishlist = f.read().splitlines()
with open(r".\wishlist_series.txt") as f:
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
    r"C:/Users/YourName/AppData/Roaming/Mozilla/Firefox/Profiles/nf1df3n1.DiscordMain",
    AccountOptions(
        roll_order=[Command.ROLL_WAIFU_ANIMANGA, Command.ROLL_ANY],
        allowed_kakera_reacts=GOOD_REACTS,
        react_emoji=Emoji.GAME_DIE,
        wishlist=wishlist,
        wishlist_series=wishlist_series,
        announcement_message=f"It's roll time! {Emoji.GAME_DIE}",
    ),
)
alt = Account(
    "alt",
    r"C:/Users/YourName/AppData/Roaming/Mozilla/Firefox/Profiles/pgddhf4x.DiscordAlt",
    AccountOptions(
        roll_order=[Command.ROLL_WAIFU_ANIMANGA, Command.ROLL_ANY],
        allowed_kakera_reacts=GOOD_REACTS,
        react_emoji=Emoji.GAME_DIE,
        wishlist=wishlist,
        wishlist_series=wishlist_series,
        announcement_message=Command.QUOT_IMAGE,
    ),
)
users = [main, alt]

my_options = ServerOptions(announce_start=True)

dev_env = Server(
    name="Dev Env",
    server_id=1111111111111,
    roll_channel_id=222222222222222222,
    minute_of_hour_to_roll=24,  # resets at 31
    accounts=users,
    options=my_options,
)
# A more lowkey configuration. Also roll only 1 account.
other_server = Server(
    name="Other Server",
    server_id=333333333333,
    roll_channel_id=444444444444444,
    minute_of_hour_to_roll=14,  # resets at 24
    accounts=[main],
    options=ServerOptions(do_daily=False, do_pokeslot=False),
)

servers = [dev_env, other_server]

if __name__ == "__main__":
    me = singleton.SingleInstance()
    logging.basicConfig(
        filename="claim_history.log", encoding="utf-8", level=logging.INFO
    )
    logging.info("Officiant starting up.")
    schedule_rolls_for_servers(servers)
