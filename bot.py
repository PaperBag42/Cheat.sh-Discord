import discord
import logging
import re
import requests
import os

from logging import log, INFO, WARN
from sys import argv, exit
from typing import Dict, List, Generator, NewType

from consts import *

ChannelID = NewType('ChannelID', int)

headers: Dict[str, str] = requests.utils.default_headers()
headers.update({
	'User-Agent': 'curl'
})

class CheatClient(discord.Client):
	'Costum discord client for cht.sh commands'
	
	shells: Dict[ChannelID, str] = {}
	
	
	async def on_ready(self):
		'Sets presence to a useful message'
		await self.change_presence(game=discord.Game(name=STATUS))
	
	
	async def on_server_join(self, server: discord.Server):
		'''
		client connected, sends a Hi message to general
		:return: None
		'''
		log(INFO, f'Successfully logged in to {server.name}')
		for channel in server.channels:
			if channel.name == 'general':
				await self.send_message(channel, HELP_MSG)
				break


	async def on_message(self, message: discord.Message):
		'''
		A message was sent, respond if needed
		:param message: message received
		:return: None
		'''
		chnl_id = ChannelID(message.channel.id)
		cmd = message.content.split('#')[0].split()
		if not cmd:
			return
		
		if cmd[0] == CWORD:
			cmd = cmd[1:]
			if not cmd or HELP in cmd:  # show help message
				await self.send_message(message.channel, HELP_MSG)
			elif cmd[0] == SHELL:  # activate shell mode
				lang = ''
				if len(cmd) >= 2:
					err = check_lang(cmd[1])
					if err:
						await self.send_message(message.channel, err)
						return
					lang = cmd[1]
				self.shells[chnl_id] = lang
				await self.send_message(message.channel, HELP_SHELL.format((' at ' + lang) if lang else ''))

			else:
				for part in process_request(cmd):
					await self.send_message(message.channel, part)
				
		elif chnl_id in self.shells and message.author.id != self.user.id:
			if cmd[0] == 'help':
				await self.send_message(message.channel, HELP_SHELL)
			elif cmd[0] == 'cd':
				if len(cmd) < 2 or cmd[1] == '..':
					self.shells[chnl_id] = ''
				else:
					err = check_lang(cmd[1])
					if err:
						await self.send_message(message.channel, err)
						return
					self.shells[chnl_id] = cmd[1]
				lang = self.shells[chnl_id]
				await self.send_message(message.channel, SHELL_CD.format(lang) if lang else SHELL_CD_OUT)
			elif cmd[0] == 'exit' or cmd[0] == 'quit':
				del self.shells[chnl_id]
				await self.send_message(message.channel, SHELL_EXIT)
			else:
				for part in process_request([self.shells[chnl_id]] + cmd):
					await self.send_message(message.channel, part)
					
	
	
def process_request(cmd: List[str]) -> Generator[str, None, None]:
	'''
	Processes request to get a cheat sheet.
	Splits response to avoid surpassing maximum length.
	'''
	res = re.sub(r'\x1b\[.+?m', '', get_cht(cmd))  # simple regex to remove color codes
	
	# cht.sh [lang] usually results in an explanation on how to install/compile/run from the terminal
	lang = LANG_ALIASES.get(cmd[0], cmd[0]) if len(cmd) > 1 else 'bash'
	max_len = MAX_LEN - len(lang) - 8  # len('```\n\n```')
				
	while res != '\n':
		part = res[:max_len]
		last = part.rfind('\n')
		if last != -1:
			part = part[:last]
		
		res = res[len(part):]
		yield f'```{lang}\n{part}\n```'



def get_cht(cmd: List[str]) -> str:
	'''
	Gets the output from the cht.sh server.
	:param cmd: input for the server
	'''
	if '--shell' in cmd:
		return 'Shell mode is not available.'

	# get a response for cmd
	response = requests.get(f"{API_URL_BASE}{cmd[0]}/{'+'.join(cmd[1:])}", headers=headers)
	if response.status_code != 200 and response.status_code != 500:
		return 'Cannot acsess cheat.sh server at the moment'
	elif response.status_code == 500:  # internal server error
		return 'Somthing is wrong with the cheat servers'
	return response.text


def check_lang(lang: str) -> str:
	'''
	Finds the language in the language list to make sure it is valid.
	:return: an empty string if valid, or an error message.
	'''
	lines = get_cht([':list']).splitlines()
	if len(lines) == 1:  # error
		return lines[0]
	
	langs = set()
	for line in lines:
		ind = line.find('/')
		if ind != -1:
			if lang == line[:ind]:
				return ''
			langs.add(line[:ind])
	return INVALID_LANG.format(lang, '\t'.join(langs))


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
