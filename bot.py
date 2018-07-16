import discord
import subprocess
import logging
import re
import requests
from sys import argv, stderr

"""
TODOs
1. find a better way to determine the programming language
2. replace comments with normal text (maybe not? it looks kinda cool how it is now)
3. make a special shell mode for specific channels
"""

client = discord.Client()

headers = requests.utils.default_headers()

headers.update(
	{
		'User-Agent': 'curl'
	}
)

CWORD = "!cht"
API_URL_BASE = 'http://cht.sh'
HELP_TEXT = """```bash
# cheat.sh, the only cheatsheet you need, is now on discord.

# Usage is similar to the cht.sh command line client:
!cht go reverse a list
!cht python random list elements
!cht js parse json

# For more information, go to:
# https://github.com/chubin/cheat.sh
# https://github.com/PaperBag42/cheat.sh-discord
```"""

@client.event
async def on_ready():
	"""
	client connected, sends a Hi message to general
	:return:None
	"""
	print("Successfully logged in as {client.user.name}".format(client=client))
	for server in client.servers:
		print(server)
		for channel in server.channels:
			print(channel)
			if channel.name == "general":
				await client.send_message(channel, HELP_TEXT)


@client.event
async def on_message(message):
	"""
	there is a massage on server, response if needed
	:param message: massage recived
	:return: None
	"""
	cmd = message.content.split()
	print(message.content)
	if cmd[0] == CWORD and len(cmd) > 1:
		# TODO #2
		# it seems that if you give cht just the programming language e.g. cht.sh python,
		# it shows you how to use it from the terminal. thats why I put the "bash".
		# there's probably a better way, maybe it will be easier after #1
		await client.send_message(message.channel, parse_cht(get_cht(cmd), cmd[1] if len(cmd) > 2 else "bash"))
	elif len(cmd) == 1:
		await client.send_message(message.channel, HELP_TEXT)


def get_cht(command):  # TODO #1
	"""
	Gets the output from the cht.sh script.
	:param command: input for the script
	"""
	if "--shell" in command:
		return "Shell mode is not available."

	if len(command) > 3:
		formated_command = '/' + command[1] + '/' + '+'.join(command[2:])
	else:
		formated_command = '/' + ''.join(command[1:])

	# get a response for command
	response = requests.get(API_URL_BASE + formated_command, headers=headers)
	if response.status_code != 200 and response.status_code != 500:
		return "Can't acsess to cheat server at the moment"
	elif response.status_code == 500: # internal server error
		return "Somthing is wrong with the cheat servers"
	return response.text


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
