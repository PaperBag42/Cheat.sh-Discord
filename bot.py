import discord
import logging
import re
import requests
import os
from sys import argv, stderr

from consts import *

"""
TODOs
1. make a special shell mode for specific channels
"""

headers = requests.utils.default_headers()
headers.update({
	'User-Agent': 'curl'
})

class CheatClient(discord.Client):
	async def on_server_join(self, server):
		"""
		client connected, sends a Hi message to general
		:return: None
		"""
		print("Successfully logged in to {}".format(server.name))
		for channel in server.channels:
			if channel.name == "general":
				await self.send_message(channel, HELP_TEXT)
				break


	async def on_message(self, message):
		"""
		there is a message on server, response if needed
		:param message: message recived
		:return: None
		"""
		cmd = message.content.split()
		if cmd[0] == CWORD:
			print("{0.author.name} sent: {0.content}".format(message))
			if '--help' in cmd:
				await self.send_message(message.channel, HELP_TEXT)
			elif len(cmd) == 1:
				await self.send_message(message.channel, HELP_TEXT)
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
								await self.send_message(message.channel, parse_cht(msg_part, get_lang(cmd))) 
								msg_part = line
								break
							else:
								msg_part += line + '\n'
					else:
						if not first:
							await self.send_message(message.channel, parse_cht(msg_part + msg, get_lang(cmd))[:-3])
						else:
							await self.send_message(message.channel, msg)
						so_far_len = len(msg) - 1
					msg = msg[so_far_len + 1:]


def get_cht(command):
	"""
	Gets the output from the cht.sh script.
	:param command: input for the script
	"""
	if "--shell" in command:
		return "Shell mode is not available."

	formated_command = command[1] + '/' + '+'.join(command[2:])

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
	token = ''
	if len(argv) > 1:
		token = argv[1]
		logging.log(logging.INFO, 'got token from command line')
	else:
		if 'TOKEN' in os.environ:
			token = os.environ.get('TOKEN')
			logging.log(logging.INFO, 'got token from env')
		else:
			print("Usage: python bot.py TOKEN", file=stderr)
	CheatClient().run(token)
