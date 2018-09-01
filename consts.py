CWORD = '!cht'
HELP = '--help'
SHELL = '--shell'

API_URL_BASE = 'http://cht.sh/'
CURL_HEADER = {'User-Agent': 'curl'}

STATUS = '!cht --help'
HELP_MSG = '''```bash
# cheat.sh, the only cheatsheet you need, is now on discord.

# Usage is similar to the cht.sh command line client:
!cht go reverse a list
!cht python random list elements
!cht js parse json

# To stop processing message: use '#'

# To display help (this page):
!cht --help

# To enter shell mode:
!cht --shell

# For more information, go to:
# https://github.com/chubin/cheat.sh
# https://github.com/PaperBag42/cheat.sh-discord
```'''
HELP_SHELL = '''```bash
# Entering shell mode{}.

help       # show this help
cd [LANG]  # change/exit the language context
exit/quit  # exit the cheat shell
```'''
SHELL_CD = '''```
Language changed to {}.
```'''
SHELL_CD_OUT = '''```
Exited language.
``'''
SHELL_EXIT = '''```
Exiting shell mode.
```'''
INVALID_LANG = '''```
Invalid section: {}
Valid sections:
{}
```'''
ERROR_MSG = '''
Something went wrong.
I will report the error, but you can still head over to <@295577662691213312> and <@367633593654050816> and punch them in the face.
'''

COLOR_CODE = r'\x1b\[.+?m'  # simple regex to remove color codes
MAX_LEN = 1990

# So what had been bothering me before was caused by the differences between Discord's programming language index (taken from highlight.js)
# and cheat.sh's. For example discord dosen't recognize python3.
# I can't see an immediate solution, so I think the best way around this is a dict of aliases.
# We can add a new alias whenever we find out about it.
LANG_ALIASES = {
	'python3': 'python'
}


# Since we're already sharing this channel on GitHub, you might as well join our server
# https://discord.gg/jJZnGW
ERRORS_CHANNEL = '485444048283238410'