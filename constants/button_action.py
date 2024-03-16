"""The buttons that can appear below a roll."""

from enum import StrEnum


class ButtonAction(StrEnum):
    WISH = "💗"
    PURPLE = "kakeraP"
    BLUE = "kakera"
    TEAL = "kakeraT"
    GREEN = "kakeraG"
    YELLOW = "kakeraY"
    ORANGE = "kakeraO"
    RED = "kakeraR"
    RAINBOW = "kakeraW"
    LIGHT = "kakeraL"


ALL_KAKERA_REACTS = [ba for ba in ButtonAction if ba.name.startswith("kakera")]
