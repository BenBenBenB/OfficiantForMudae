# Officiant for Mudae

Is marrying waifus in Mudae too much work? Let the Officiant do the marrying for you.

This is written in python (tested in 3.11 only) and uses Selenium to launch Discord via headless instances of Firefox and perform actions you would typically do for your hourly rolls for the Mudae bot.

:warning: **Self-botting is against Discord's ToS.** By using this, you recognize that there is a potential risk that any Discord accounts involved may be banned. Proceed with caution. :warning:

**Features**

- Reads your `$tu` message to do dailies, pokeslot, and rolls accordingly
- Specify characters and series to be automatically claimed
- Specify minimum kakera value and/or max claim rank for greedy claims.
- Attempts to `$rt` if needed to claim your own wishes.
- Automatically react to kakera, and filter out the low tier ones.
- Claims your own wishes ASAP, waits to claim others. 
- Automatically claim the best available character if it is the end of the claim period.
    - Prioritized by wishes, then kakera value.

## Basic Usage
### Firefox Profiles
A Firefox profile must be set up for each account. To do this:
1. Navigate to `about:profiles` in firefox
1. Create a New Profile. Enter your preferred name and save directory.
1. Note the `Root Directory` for the profile. This path is used to point Selenium to this instance.
1. Launch the profile and sign in to your Discord account on [their web app](https://discord.com/app)

### Set up Python
This will (might) eventually be packaged. For now these steps must be taken. The eastiest way is propbably to [set up a venv in Visual Studio Code](https://code.visualstudio.com/docs/python/environments).
1. Set up python 3.11
1. install packages with `pip install packagename`
    - `pip install selenium`
    - `pip install retry`
    - `pip install tendo`
1. Run the script
    - `python main.py`

### Configuration
- Create an instance of `Account` for each Discord account you intend to roll with.
    - You can set wishlists, acceptable kakera reacts, and more with the `AccountOptions` parameter
- Create an instance of `Server` for each server you intend to roll on.
    - specify the `Root Directory` of the relevant Firefox profile here
    - Obtain the server id and channel/thread id by either
        - Visiting the web app and obtaining the values from the URL
        - Activate Developer Mode and copy the ids via the context menu
    - Specify the list of users that should roll on this server
    - You can set whether to pokeslot, dk, etc with the `ServerOptions` parameter

