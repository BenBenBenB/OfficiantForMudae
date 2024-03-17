import logging
from operator import attrgetter
import re
from retry import retry
from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from time import sleep

from constants import (
    ALL_KAKERA_REACTS,
    ButtonAction,
    Command,
    Emoji,
    MessageSource,
    TuRow,
    Wait,
)
import exceptions as exc

DEFAULT_EMOJI = Emoji.GAME_DIE
UNCLAIMED_MESSAGE = "React with any emoji to claim!"


class DiscordElement: ...


class AccountOptions:
    roll_order: list[Command]
    allowed_kakera_reacts: list[ButtonAction]
    wishlist: list[str]
    wishlist_series: list[str]
    greed_threshold_kakera: int
    greed_threshold_rank: int
    react_emoji: Emoji
    announcement_message: str

    def __init__(
        self,
        roll_order: list[Command] = [Command.ROLL_ANY],
        allowed_kakera_reacts: list[ButtonAction] = [ALL_KAKERA_REACTS],
        wishlist: list[str] = [],
        wishlist_series: list[str] = [],
        greed_threshold_kakera=9999,
        greed_threshold_rank=0,
        react_emoji=DEFAULT_EMOJI,
        announcement_message="",
    ) -> None:
        self.roll_order = roll_order
        self.allowed_kakera_reacts = allowed_kakera_reacts
        self.wishlist = wishlist
        self.wishlist_series = wishlist_series
        self.greed_threshold_kakera = greed_threshold_kakera
        self.greed_threshold_rank = greed_threshold_rank
        self.react_emoji = react_emoji
        self.announcement_message = announcement_message


class Account:
    """Holds Discord account access and settings.
    name: A friendly name, for logging.
    firefox_profile: path to specific firefox profile directory
    options: customization options for rolls, reacts, etc.
    """

    name: str
    firefox_profile: str
    options: AccountOptions

    def __init__(
        self,
        name: str,
        firefox_profile: str,
        options: AccountOptions = AccountOptions(),
    ):
        self.name = name
        self.firefox_profile = firefox_profile
        self.options = options

    def get_firefox_browser(self) -> WebDriver:
        ffOptions = Options()
        ffOptions.add_argument("-profile")
        ffOptions.add_argument(self.firefox_profile)
        browser = webdriver.Firefox(options=ffOptions)
        browser.implicitly_wait(Wait.DEFAULT_TIME_OUT)
        return browser


class MessageBox:
    _driver: WebDriver
    element: WebElement
    sent_by: str

    def __init__(self, driver: WebDriver) -> None:
        self._driver = driver
        try:
            self.element = driver.find_element(By.XPATH, "//div[@role='textbox']")
        except NoSuchElementException as e:
            raise exc.MessageBoxNotFoundException(
                "Unable to find message box element."
            ) from e

    def send(self, text: str, param: str | None = None) -> None:
        self._clear_text()
        self.element.send_keys(Keys.ESCAPE)
        if text.startswith("/"):
            self._send_command(text, param)
        else:
            self.element.send_keys(text + Keys.RETURN)

    def _clear_text(self) -> None:
        action = ActionChains(self._driver)
        action.move_to_element(self.element)
        action.key_down(Keys.CONTROL).send_keys("A").key_up(Keys.CONTROL)
        action.send_keys(Keys.BACKSPACE)
        action.perform()

    def _send_command(self, command: str, param: str | None):
        command = command.lstrip("/")
        if not command.endswith(" "):
            command += " "
        self.element.send_keys("/")
        self._wait_for_slash_to_be_recognized()
        self.element.send_keys(command)
        self._wait_for_command_to_be_recognized()
        if param:
            self.element.send_keys(param)
        self.element.send_keys(Keys.RETURN)

    @retry(NoSuchElementException, 3)
    def _wait_for_slash_to_be_recognized(self):
        self._driver.find_element(
            By.XPATH, "//div[starts-with(@class, 'autocomplete_')]"
        )

    @retry(NoSuchElementException, 3)
    def _wait_for_command_to_be_recognized(self):
        self._driver.find_element(
            By.XPATH, "//div[starts-with(@class, 'attachedBars_')]"
        )

    def get_timers_up(self):
        self._send_command("/tu")


class Message:
    _driver: WebDriver
    _channel: "Channel"
    message_id: int
    element: WebElement
    source: MessageSource
    invoked_by: str
    command: Command | None
    content: str

    @property
    def id(self):
        return f"chat-messages-{self._channel._channel_id}-{id}"

    def __init__(
        self, driver: WebDriver, channel: "Channel", element: WebElement
    ) -> None:
        self._driver = driver
        self._channel = channel
        self.element = element
        self.message_id = element.get_attribute("id").split("-")[-1]
        text_lines = element.text.split("\n")
        self.command, self.invoked_by = None, None
        if len(text_lines) == 1:
            self.source = MessageSource.TEXT
        elif text_lines[1] == " used ":
            self.invoked_by = text_lines[0]
            self.source = MessageSource.SLASH_COMMAND
            try:
                self.command = Command(text_lines[2])
            except Exception:
                self.command = Command.UNKNOWN
            text_lines = text_lines[6:]
        elif text_lines[1] == "BOT":
            self.source = MessageSource.TEXT_COMMAND
            text_lines = text_lines[3:]
        else:
            self.source = MessageSource.TEXT
            text_lines = text_lines[2:]
        self.content = "\n".join(text_lines)

    def get_fresh(self) -> "Message":
        return self._channel.get_message_by_id(self.message_id)

    def react(self, emoji: Emoji):
        js_code = "arguments[0].scrollIntoView();"
        self._driver.execute_script(js_code, self.element)

        action = ActionChains(self._driver)
        action.move_to_element(self.element)
        action.context_click()
        action.perform()

        add_reaction = self._driver.find_element(
            By.XPATH, "//div[@id='message-add-reaction']"
        )
        add_reaction.click()

        emoji_search = self._driver.find_element(
            By.XPATH, "//input[@aria-label='Search emoji']"
        )
        emoji_search.send_keys(emoji)

        emoji_text = emoji.value.strip(":")
        emoji_button = self._driver.find_element(
            By.XPATH, f"//button[contains(@data-name,'{emoji_text}')]"
        )
        emoji_button.click()


class MudaeButton:
    _element: WebElement
    action: ButtonAction

    def __init__(self, element: WebElement) -> None:
        self._element = element
        self.action = ButtonAction(element.accessible_name)

    @retry(ElementClickInterceptedException, 5, Wait.SPAM_REACT)
    def click(self) -> None:
        self._element.click()


class CharacterRoll:
    _browser: WebDriver
    _message: Message
    name: str
    series: str
    rank: int
    kakera: int
    claimed: bool
    owner: str
    wished: bool
    wished_by: list[str]
    kakera_reacts: list[MudaeButton]  # the buttons

    @property
    def claimed(self):
        return self.owner is not None

    @property
    def message_id(self):
        return self._message.message_id

    @property
    def id(self):
        return self._message.id

    def __init__(self, browser: WebDriver, message: Message):
        if (
            message is None
            or message.command is None
            or not message.command.name.startswith("ROLL")
        ):
            raise TypeError("Supplied message is not roll slash command response")

        self._browser = browser
        self._message = message
        lines: list[str] = message.content.split("\n")

        self.wished = lines[0].startswith("Wished by ")
        self.wished_by = self._set_wished_by(lines.pop(0)) if self.wished else []

        self.name = lines.pop(0)

        try:
            owner_index = next(
                index
                for index, value in enumerate(lines)
                if value.startswith("Belongs to ")
            )
            self.owner = lines.pop(owner_index)[len("Belongs to ") :]
        except StopIteration:
            self.owner = None

        try:
            rank_index = next(
                index
                for index, value in enumerate(lines)
                if value.startswith("Claims: #")
            )
            self.rank = int(
                "".join(char for char in lines.pop(rank_index) if char.isnumeric())
            )
        except StopIteration:
            self.rank = 999999

        try:
            kakera_index = next(
                index for index, value in enumerate(lines) if value.isnumeric()
            )
            self.kakera = int(lines.pop(kakera_index))
        except StopIteration:
            self.kakera = 0

        if lines:
            if re.match(r".*\/.*- \d+ ka", lines[-1]):
                lines.pop()
            if lines[-1] == UNCLAIMED_MESSAGE:
                lines.pop()
            self.series = " ".join(line for line in lines if line)
        else:
            self.series = "Meme"

        self._set_buttons()

    @property
    def footer(self):
        return f"{self.name} / {self.series} - {self.kakera}"

    def __str__(self) -> str:
        return f"#{self.rank} {self.footer}"

    def _set_wished_by(self, text: str) -> None:
        if text.endswith("(edited)"):
            text = text[0:-10]
        return [name.strip() for name in text.split(",")]

    def _set_buttons(self) -> None:
        buttons = [MudaeButton(b) for b in self._get_button_elements()]
        if self.wished:
            self.wish_react = next(b for b in buttons if b.action == ButtonAction.WISH)
        self.kakera_reacts = [b for b in buttons if b.action != ButtonAction.WISH]
        pass

    def claim(self, emoji=DEFAULT_EMOJI) -> None:
        logging.info(f"Attempting claim for: {self}")
        self.react(emoji)
        pass

    def _get_button_elements(self) -> list[WebElement]:
        sleep(Wait.LOAD_BUTTON)
        return self._message.element.find_elements(
            By.XPATH, ".//button[@role='button']"
        )

    def react(self, emoji: Emoji = DEFAULT_EMOJI):
        self._message.react(emoji)

    def get_fresh(self) -> "CharacterRoll":
        return CharacterRoll(self._browser, self._message.get_fresh())


class Channel:
    _driver: WebDriver
    _server_id: int
    _channel_id: int
    _message_box: MessageBox

    def __init__(self, driver: WebDriver, server_id: int, channel_id: int) -> None:
        self._driver = driver
        self._server_id = server_id
        self._channel_id = channel_id
        self._message_box = MessageBox(driver)

    def send(self, text: str, params: str | None = None) -> Message:
        """Sends inputs to the message box and returns the response."""
        input_command, input_source = self._characterize_input(text)

        self._message_box.send(text, params)
        latest_message = self.get_latest_message()
        sleep(Wait.MESSAGE_LOAD)
        while (
            input_source == MessageSource.SLASH_COMMAND
            and latest_message.source == MessageSource.SLASH_COMMAND
            and latest_message.content in ["", "Sending command..."]
        ):
            latest_message = self.get_latest_message()
        # Handle other messages that may have appeared while waiting
        if input_command and input_command != latest_message.command:
            latest_message = next(
                message
                for message in self.get_messages()[::-1]
                if message.command == input_command
            )
        if "Command DISABLED for this channel" in latest_message.content:
            raise exc.CommandDisabledException()

        return latest_message

    @retry(StaleElementReferenceException, tries=4)
    def get_messages(self) -> list[Message]:
        return [
            Message(self._driver, self, message_element)
            for message_element in self._driver.find_elements(
                By.XPATH, "//li[starts-with(@id, 'chat-messages')]"
            )
        ]

    @retry(StaleElementReferenceException, tries=2, delay=Wait.MESSAGE_LOAD)
    def get_latest_message(self) -> Message:
        latest_message_element = self._driver.find_elements(
            By.XPATH, "//li[starts-with(@id, 'chat-messages')]"
        )[-1]
        return Message(self._driver, self, latest_message_element)

    def get_message_by_id(self, message_id: int):
        return self.get_message_by_html_id(self.get_html_message_id(message_id))

    def get_html_message_id(self, message_id: int) -> str:
        return f"chat-messages-{self._channel_id}-{message_id}"

    def get_message_by_html_id(self, id: str):
        try:
            return Message(
                self._driver,
                self,
                self._driver.find_element(By.XPATH, f"//li[@id='{id}']"),
            )
        except NoSuchElementException:
            return None

    def parse_message(self, web_element: WebElement):
        return Message(self._driver, self, self, web_element)

    def _characterize_input(self, text):
        try:
            input_command = Command(text)
            input_source = (
                MessageSource.SLASH_COMMAND
                if input_command.value.startswith("/")
                else MessageSource.TEXT_COMMAND
            )
        except ValueError:
            input_command = None
            input_source = MessageSource.TEXT
        return input_command, input_source


class TimersUp:
    """Requires this tu arrange command be used on each account:
    $ta claim, rolls, rt, rollsreset, jump, kakerareact, kakerapower, kakerainfo, kakerastock, jump, dk, daily, vote, pokemon

    Example:
        {name}, you can claim right now! The next claim reset is in 2h 21 min.
        You have 12 rolls left. Next rolls reset in 21 min.
        $rt is available!
        You have 64 rolls reset in stock.

        You can react to kakera right now!
        Power: 77%
        Each kakera reaction consumes 34% of your reaction power.
        Your characters with 10+ keys consume half the power (17%)
        Stock: 101637:kakera:

        $dk is ready!
        Next $daily reset in 6h 36 min.
        You may vote again in 15 min.
        Remaining time before your next $p: 59 min.
    """

    can_claim: bool
    can_rt: bool
    can_daily_kakera: bool
    can_daily: bool
    can_pokeslot: bool
    claim_reset_minutes: int
    rolls_left: int
    mk_rolls_left: int
    rolls_reset: int
    kakera_stock: int
    kakera_power: int
    kakera_cost: int

    @property
    def is_claim_hour(self):
        return self.claim_reset_minutes <= 60

    @property
    def can_react(self):
        return self.kakera_power >= self.kakera_cost

    def __init__(self, tu_message: Message) -> None:
        if tu_message.command != Command.TIMERS_UP:
            raise exc.InvalidTimersUpMessageException(
                f"Expecting {Command.TIMERS_UP} but received {tu_message.command}"
            )
        lines = self._cleanse_response(tu_message.content)

        self.can_claim = "you can claim right now" in lines[TuRow.CLAIM]
        self.can_rt = lines[TuRow.RESET_CLAIM_TIMER] == "rt is available"
        self.can_daily_kakera = lines[TuRow.DAILY_KAKERA] == "dk is ready"
        self.can_daily = lines[TuRow.DAILY] == "daily is available"
        self.can_pokeslot = lines[TuRow.POKESLOT] == "p is available"
        self.claim_reset_minutes = self._extract_minutes(lines[TuRow.CLAIM][-9:])
        self.rolls_left = self._extract_int(lines[TuRow.ROLLS][9:11])
        self.mk_rolls_left = self._extract_int(lines[TuRow.ROLLS][17:25])
        self.rolls_reset_stock = self._extract_int(lines[TuRow.ROLLS_RESET])
        self.kakera_stock = self._extract_int(lines[TuRow.KAKERA_STOCK])
        self.kakera_power = self._extract_int(lines[TuRow.KAKERA_POWER])
        self.kakera_cost = self._extract_int(lines[TuRow.KAKERA_COST])

        pass

    def _cleanse_response(self, tu_command_response: str) -> list[str]:
        cleaned = re.sub(r"[^a-z0-9 \n]", "", tu_command_response.lower())
        return [line.strip() for line in cleaned.splitlines()]

    def _extract_int(self, input) -> int:
        return int("0" + re.sub("[^0-9]", "", input).strip())

    def _extract_minutes(self, displayed_time) -> int:
        times = [int(t) for t in re.sub(r"[^0-9 ]", "", displayed_time).split(" ") if t]
        if len(times) == 1:
            return times[0]
        else:
            return times[0] * 60 + times[1]


def get_best_waifu(rolls: list[CharacterRoll]) -> CharacterRoll:
    return max(rolls, key=attrgetter("kakera"))


class ServerOptions:
    do_react: bool
    do_daily: bool
    do_daily_kakera: bool
    do_pokeslot: bool
    announce_start: bool

    def __init__(
        self,
        do_react: bool = True,
        do_daily: bool = True,
        do_daily_kakera: bool = True,
        do_pokeslot: bool = True,
        announce_start: bool = False,
    ) -> None:
        self.do_react = do_react
        self.do_daily = do_daily
        self.do_daily_kakera = do_daily_kakera
        self.do_pokeslot = do_pokeslot
        self.announce_start = announce_start


class Server:
    """Contains config for rolling on a server."""

    name: str
    server_id: int
    roll_channel_id: int
    minute_of_hour_to_roll: int
    accounts: list[Account]
    options: ServerOptions

    @property
    def url(self):
        return f"https://discord.com/channels/{self.server_id}/{self.roll_channel_id}"

    def __init__(
        self,
        name: str,
        server_id: int,
        roll_channel_id: int,
        minute_of_hour_to_roll: int,
        accounts: list[Account],
        options: ServerOptions = ServerOptions(),
    ):
        self.name = name
        self.server_id = server_id
        self.roll_channel_id = roll_channel_id
        self.minute_of_hour_to_roll = minute_of_hour_to_roll
        self.accounts = accounts
        self.options = options

    def do_rolls(self):
        logging.info(f"Rolling on server {self.name} {self.url}")
        for user in self.accounts:
            try:
                browser = user.get_firefox_browser()
                self._process_user(browser, user)
            except Exception:
                logging.error(f"Problem processing user {user.name}", exc_info=True)
            browser.quit()

    def _process_user(self, browser: WebDriver, user: Account):
        logging.info(f"Starting user {user.name}")
        browser.get(self.url)
        sleep(Wait.PAGE_LOAD)
        # todo: wait for latest message in channel to be 15s or older
        roll_channel = Channel(browser, self.server_id, self.roll_channel_id)
        roll_channel.send(Keys.ESCAPE * 2)
        if user.options.announcement_message and self.options.announce_start:
            roll_channel.send(user.options.announcement_message)
        try:
            tu = self.get_timers_up(roll_channel, user)
        except exc.InvalidTimersUpException:
            roll_channel.send("Oops sorry!")
        self._do_non_rolls(roll_channel, tu)

        self._do_rolls(
            browser, roll_channel, tu, user, tu.mk_rolls_left, [Command.ROLL_KAKERA]
        )
        rolled = self._do_rolls(
            browser, roll_channel, tu, user, tu.rolls_left, user.options.roll_order
        )

        if tu.rolls_left > 0:
            tu = self.get_timers_up(roll_channel, user)
        if rolled and tu.is_claim_hour and tu.can_claim:
            self.claim_best_available(rolled)

    def claim_best_available(self, rolls: list[CharacterRoll]):
        best_choice = None
        while best_choice is None or best_choice.claimed:
            best_choice = get_best_waifu(rolls)
            rolls.remove(best_choice)
            best_choice = best_choice.get_fresh()
        best_choice.claim()

    @retry(exc.InvalidTimersUpException, 2)
    def get_timers_up(self, channel: Channel, user: Account, is_retry_after_ta=False):
        try:
            response = channel.send("/tu")
            # prevent someone else's tu from being read
            name_on_tu = response.content.split(",")[0]
            if user.name != name_on_tu:
                raise exc.InvalidTimersUpException(user.name, name_on_tu)
            return TimersUp(response)
        except IndexError as e:
            if not is_retry_after_ta:
                channel.send(Command.TIMERS_UP_ARRANGE, Command.TIMERS_UP_ARRANGE_PARAM)
                return self.get_timers_up(channel, user, True)
            else:
                channel.send("Oops")
                raise e

    def _do_non_rolls(self, channel: Channel, tu: TimersUp) -> None:
        if self.options.do_daily and tu.can_daily:
            channel.send(Command.DAILY)
        if (
            self.options.do_daily_kakera
            and tu.can_daily_kakera
            and not tu.can_react  # todo: smarter dk
        ):
            channel.send(Command.DAILY_KAKERA)
        if self.options.do_pokeslot and tu.can_pokeslot:
            channel.send(Command.POKESLOT)

    def _do_rolls(
        self,
        browser: WebDriver,
        channel: Channel,
        tu: TimersUp,
        user: Account,
        count: int,
        roll_order: list[Command],
    ) -> list[CharacterRoll]:
        rolled = []
        for i in range(count):
            command = roll_order[i % len(roll_order)]
            just_rolled = CharacterRoll(browser, channel.send(command))
            rolled.append(just_rolled)
            if just_rolled.wished and not just_rolled.claimed:
                logging.info(f"Claiming wish for {user.name}: {just_rolled.name}")
                just_rolled.wish_react.click()
                just_rolled.claimed = True
                continue
            if just_rolled.kakera_reacts:
                good_reacts = [
                    b
                    for b in just_rolled.kakera_reacts
                    if b.action in user.options.allowed_kakera_reacts
                ]
                for react_button in good_reacts:
                    react_button.click()
            if not just_rolled.claimed and (
                just_rolled.name in user.options.wishlist
                or just_rolled.series in user.options.wishlist_series
                or just_rolled.rank <= user.options.greed_threshold_rank
                or just_rolled.kakera >= user.options.greed_threshold_kakera
            ):
                logging.info(f"Claiming for {user.name}: {just_rolled.name}")
                just_rolled.claim(user.options.react_emoji)
                just_rolled.claimed = True

        return rolled
