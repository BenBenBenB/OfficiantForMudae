import logging
import sched
import time
import datetime
from discord_elements import Server


def get_seconds_until_minute_of_hour(
    minute_of_hour: int, starting_up: bool
) -> datetime.timedelta:
    now = datetime.datetime.now()
    if now.minute == minute_of_hour and starting_up:  # helps debug faster
        return 0
    later = datetime.datetime.now()
    later = later.replace(minute=minute_of_hour, second=0)
    if later <= now:
        later += datetime.timedelta(hours=1)
    return (later - now).seconds


def schedule_rolls(
    scheduler: sched.scheduler, server: Server, starting_up: bool = True
):
    seconds_to_wait = get_seconds_until_minute_of_hour(
        server.minute_of_hour_to_roll, starting_up
    )
    logging.info(f"Scheduled '{server.name}' for {seconds_to_wait} seconds from now")
    scheduler.enter(seconds_to_wait, 1, server.do_rolls, ())
    scheduler.enter(seconds_to_wait, 2, schedule_rolls, (scheduler, server, False))
    pass


def schedule_rolls_for_servers(servers: list[Server]):
    scheduler = sched.scheduler(time.time, time.sleep)
    for server in servers:
        schedule_rolls(scheduler, server)
    scheduler.run()


__all__ = [schedule_rolls_for_servers]
