"""helps index to the output of $tu command.
accounts need to have the following $tuarrange:
$ta claim, rolls, rt, rollsreset, jump, kakerareact, kakerapower, kakerainfo, kakerastock, jump, dk, daily, vote, pokemon
"""

from enum import IntEnum


class TuRow(IntEnum):
    CLAIM = 0
    ROLLS = 1
    RESET_CLAIM_TIMER = 2
    ROLLS_RESET = 3

    KAKERA_REACT = 5
    KAKERA_POWER = 6
    KAKERA_COST = 7
    KAKERA_STOCK = 9

    DAILY_KAKERA = 11
    DAILY = 12
    VOTE = 13
    POKESLOT = 14
