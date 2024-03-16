"""the slash commands to be used"""

from enum import StrEnum


class Command(StrEnum):
    TIMERS_UP = "/tu"
    TIMERS_UP_ARRANGE = "/rollsutil tuarrange"
    TIMERS_UP_ARRANGE_PARAM = "claim, rolls, rt, rollsreset, jump, kakerareact, kakerapower, kakerainfo, kakerastock, jump, dk, daily, vote, pokemon"
    POKESLOT = "/pokeslot"
    RESET_CLAIM_TIMER = "/rollsutil resetclaimtimer"
    DAILY = "/daily"
    DAILY_KAKERA = "/kakera dailyk"
    ROLL_KAKERA = "/mk"

    ROLL_ANY = "/mx"
    ROLL_ANY_ANIMANGA = "/ma"
    ROLL_ANY_GAME = "/mg"

    ROLL_WAIFU = "/wx"
    ROLL_WAIFU_ANIMANGA = "/wa"
    ROLL_WAIFU_GAME = "/wg"

    ROLL_HUSBANDO = "/hx"
    ROLL_HUSBANDO_ANIMANGA = "/ha"
    ROLL_HUSBANDO_GAME = "/hg"
