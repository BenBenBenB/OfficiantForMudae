"""The ways of interacting with Discord via the text area."""

from enum import Enum


class MessageSource(Enum):
    TEXT = 1
    TEXT_COMMAND = 2
    SLASH_COMMAND = 3
