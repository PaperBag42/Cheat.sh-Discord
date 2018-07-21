import discord
import logging
import re
import requests
from sys import argv, stderr

from consts import *

"""
TODOs
1. make a special shell mode for specific channels
"""

client = discord.Client()

headers = requests.utils.default_headers()
headers.update({
	'User-Agent': 'curl'
})

@client.event
async def on_ready():
	"""
	client connected, sends a Hi message to general
	:return: None
	"""
	print("Successfully logged in as {}".format(client.user.name))
	for server in client.servers:
		for channel in server.channels:
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
	if cmd[0] == CWORD:
		print("{0.author.name} sent: {0.content}".format(message))
		if '--help' in cmd:
			await client.send_message(message.channel, HELP_TEXT)
		elif len(cmd) == 1:
			await client.send_message(message.channel, HELP_TEXT)
		else:
			msg = parse_cht(get_cht(cmd), get_lang(cmd))
			first = True
			while msg:
				so_far_len = 0
				if len(msg) > MAX_LEN:
					first = False
					msg_part = ''
					for line in msg.split('\n'):
						so_far_len += len(line) + 1 
						if so_far_len >= MAX_LEN:
							print('From line 65')
							await client.send_message(message.channel, parse_cht(msg_part, get_lang(cmd))) 
							break
						else:
							msg_part += line + '\n'
				else:
					if not first:
						print('From line 73')
						await client.send_message(message.channel, parse_cht(msg, get_lang(cmd))[:-3])
					else:
						print('From line 76')
						await client.send_message(message.channel, msg)
					so_far_len = len(msg) - 1
				msg = msg[so_far_len + 1:]


def get_cht(command):
	"""
	Gets the output from the cht.sh script.
	:param command: input for the script
	"""
	if "--shell" in command:
		return "Shell mode is not available."

	if len(command) > 3:
		formated_command = command[1] + '/' + '+'.join(command[2:])
	else:
		formated_command = '/'.join(command[1:])

	# get a response for command
	response = requests.get(API_URL_BASE + formated_command, headers=headers)
	if response.status_code != 200 and response.status_code != 500:
		return "Can't acsess to cheat server at the moment"
	elif response.status_code == 500: # internal server error
		return "Somthing is wrong with the cheat servers"
	return response.text


def get_lang(command):
	"""
	Gets the name of the relevant programming language.
	:param command: input for the script
	"""
	if len(command) < 3: # cht.sh [lang] usually results in an explanation on how to install/compile/run from the terminal
		return "bash"
	return LANG_ALIASES.get(command[1], command[1])


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
	logging.basicConfig(level=logging.WARN)
	if len(argv) > 1:
		client.run(argv[1])
	else:
		print("Usage: python bot.py TOKEN", file=stderr)
		# this gives "unclosed client session" but I think we can ignore that
