import discord
import subprocess
import logging
import re
from sys import argv, stderr

"""
TODOs
1. get cheats with http instead of the shell script
2. find a better way to determine the programming language
3. replace comments with normal text
"""

client = discord.Client()

CWORD = "!cht"


@client.event
async def on_ready():
	print('Logged in as')
	print(client.user.name)
	print(client.user.id)
	print('------')


@client.event
async def on_message(message):
	cmd = message.content.split()
	
	if cmd[0] == CWORD:
		await client.send_message(message.channel, parse_cht(get_cht(cmd), cmd[1] if len(cmd) > 2 else "bash"))


def get_cht(command):
	return subprocess.run(
		["cht.sh"] + command[1:],
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT
	).stdout.decode()


def parse_cht(text, lang):
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
