# sd-helper
A bot to automatically post useful information on the SecureDrop Gitter room. Messages can be scheduled to be posted on specific day(s) of the week at specific time(s). It can be used in any other Gitter room as well.

## Requirements

1. Python [Requests](http://docs.python-requests.org/en/master/)

    `pip3 install requests`

2. Python [schedule](https://schedule.readthedocs.io/en/stable/)

    `pip3 install schedule`
    
## Usage

1. Sign in with a Github account on https://developer.gitter.im/ to obtain the authentication token required to access the Gitter API.

2. Clone the repo, and `cd` into it.

3. Create a file **auth.yml** with its contents as

`apitoken: <gitter-api-token>`

4. Run `python3 main.py` to start the bot.
