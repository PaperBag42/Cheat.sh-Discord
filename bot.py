import discord
import subprocess
import logging
import re
from sys import argv, stderr

"""
TODOs
1. get cheats with http instead of the shell script
2. find a better way to determine the programming language
3. replace comments with normal text (maybe not? it looks kinda cool how it is now)
4. make a special shell mode for specific channels
"""

client = discord.Client()

CWORD = "!cht"


@client.event
async def on_ready():
	print("Successfully logged in as {client.user.name}".format(client=client))
	for server in client.servers:
		print(server)
		for channel in server.channels:
			print(channel)
			if channel.name == "general":
				await client.send_message(channel, """```bash
# cheat.sh, the only cheatsheet you need, is now on discord.

# Usage is similar to the cht.sh command line client:
!cht go reverse a list
!cht python random list elements
!cht js parse json

# For more information, go to:
# https://github.com/chubin/cheat.sh
# https://github.com/PaperBag42/cheat.sh-discord
```""")


@client.event
async def on_message(message):
	cmd = message.content.split()
	print(message)
	if cmd[0] == CWORD:
		# TODO #2
		# it seems that if you give cht just the programming language e.g. cht.sh python,
		# it shows you how to use it from the terminal. thats why I put the "bash".
		# there's probably a better way, maybe it will be easier after #1
		await client.send_message(message.channel, parse_cht(get_cht(cmd), cmd[1] if len(cmd) > 2 else "bash"))


def get_cht(command):  # TODO #1
	"""
	Gets the output from the cht.sh script.
	:param command: input for the script
	"""
	if command[1] == "--shell":
		return "Shell mode is not available."
	return subprocess.run(
		["cht.sh"] + command[1:],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT
	).stdout.decode()


def parse_cht(text, lang):
	"""
	Removes the terminal color codes and applies Discord's highlighting
	:param text: the text to highlight
	:param lang: name of the programming language to highlight the text by
	:return: the formatted text
	"""
	return "```{lang}\n{code}\n```".format(
		lang=lang,
		code=re.sub(r"\x1b\[.+?m", "", text)  # simple regex to remove color codes
	)
	

if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	if len(argv) > 1:
		client.run(argv[1])
	else:
		print("Usage: python bot.py TOKEN", file=stderr)
		# this gives "unclosed client session" but I think we can ignore that
