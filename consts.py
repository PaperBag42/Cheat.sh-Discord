CWORD = '!cht'
HELP = '--help'
SHELL = '--shell'

API_URL_BASE = 'http://cht.sh/'

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

MAX_LEN = 1990

# So what had been bothering me before was caused by the differences between Discord's programming language index (taken from highlight.js)
# and cheat.sh's. For example discord dosen't recognize python3.
# I can't see an immediate solution, so I think the best way around this is a dict of aliases.
# We can add a new alias whenever we find out about it.
LANG_ALIASES = {
	'python3': 'python'
}