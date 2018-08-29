import discord
import logging
import re
import requests
import os

from logging import log, INFO, WARN
from sys import argv, exit

from consts import *

'''
TODOs
1. make a special shell mode for specific channels
'''

headers = requests.utils.default_headers()
headers.update({
	'User-Agent': 'curl'
})

class CheatClient(discord.Client):
	async def on_server_join(self, server):
		'''
		client connected, sends a Hi message to general
		:return: None
		'''
		print(f'Successfully logged in to {server.name}')
		for channel in server.channels:
			if channel.name == 'general':
				await self.send_message(channel, HELP_TEXT)
				break


	async def on_message(self, message):
		'''
		A message was sent, respond if needed
		:param message: message received
		:return: None
		'''
		cmd = message.content.split()
		if cmd[0] == CWORD:
			print('{0.author.name} sent: {0.content}'.format(message))
			if '--help' in cmd or len(cmd) == 1:
				await self.send_message(message.channel, HELP_TEXT)
			else:
				# cht.sh [lang] usually results in an explanation on how to install/compile/run from the terminal
				lang = LANG_ALIASES.get(cmd[1], cmd[1]) if len(cmd) > 2 else 'bash'
				max_len = MAX_LEN - len(lang) - 8
				msg = re.sub(r'\x1b\[.+?m', '', get_cht(cmd))  # simple regex to remove color codes
				
				# splits response to avoid surpassing maximum length
				while msg != '\n':
					part = msg[:max_len]
					last = part.rfind('\n')
					if last != -1:
						part = part[:last]
					
					await self.send_message(message.channel, f'```{lang}\n{part}\n```')
					msg = msg[len(part):]


def get_cht(command):
	'''
	Gets the output from the cht.sh script.
	:param command: input for the script
	'''
	if '--shell' in command:
		return 'Shell mode is not available.'

	formated_command = command[1] + '/' + '+'.join(command[2:])

	# get a response for command
	response = requests.get(API_URL_BASE + formated_command, headers=headers)
	if response.status_code != 200 and response.status_code != 500:
		return 'Cannot acsess cheat.sh server at the moment'
	elif response.status_code == 500:  # internal server error
		return 'Somthing is wrong with the cheat servers'
	return response.text
	

if __name__ == '__main__':
	logging.basicConfig(level=WARN)
	
	if len(argv) > 1:
		token = argv[1]
		log(INFO, f'Got token from command line: {token}')
	elif 'TOKEN' in os.environ:
		token = os.environ.get('TOKEN')
		log(INFO, f'Got token from env: {token}')
	else:
		log(INFO, 'Usage: python bot.py TOKEN')
		exit(1)
	
	try:
		CheatClient().run(token)
	except discord.errors.LoginFailure:
		log(logging.ERROR, 'Fatal: Invalid token.')
		exit(1)
