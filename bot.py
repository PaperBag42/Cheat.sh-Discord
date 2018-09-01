import discord
import logging
import re

from logging import log, INFO
from typing import Dict, List, NewType

from util import get_cht, check_lang
from consts import *


ChannelID = NewType('ChannelID', int)


class CheatClient(discord.Client):
	'Costum discord client for cht.sh commands'
	
	shells: Dict[ChannelID, str] = {}
	
	
	async def on_ready(self):
		'''
		Sets presence to a useful message.
		:return: None
		'''
		await self.change_presence(game=discord.Game(name=STATUS))
	
	
	async def on_server_join(self, server: discord.Server):
		'''
		Client connected, sends a Hi message to general
		:param server: the server the client just joined to
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
		:param message: the received message
		:return: None
		'''
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
				self.shells[ChannelID(message.channel.id)] = lang
				await self.send_message(message.channel, HELP_SHELL.format((' at ' + lang) if lang else ''))

			else:
				await self._process_request(cmd, message.channel)
				
		elif message.channel.id in self.shells and message.author.id != self.user.id:  # in shell mode
			await self._handle_shell(cmd, message.channel)
	
	
	async def _handle_shell(self, cmd: List[str], chnl: discord.Channel):
		'''
		Handles commands in shell mode.
		:param cmd: the received command
		:param chnl: the channel the command was sent from
		:return: None
		'''
		if cmd[0] == 'help':
			await self.send_message(chnl, HELP_SHELL)
		elif cmd[0] == 'cd':
			if len(cmd) < 2 or cmd[1] == '..':
				self.shells[chnl.id] = ''
			else:
				err = check_lang(cmd[1])
				if err:
					await self.send_message(chnl, err)
					return
				self.shells[chnl.id] = cmd[1]
			lang = self.shells[chnl.id]
			await self.send_message(chnl, SHELL_CD.format(lang) if lang else SHELL_CD_OUT)
		elif cmd[0] == 'exit' or cmd[0] == 'quit':
			del self.shells[chnl.id]
			await self.send_message(chnl, SHELL_EXIT)
		else:
			await self._process_request([self.shells[chnl.id]] + cmd, chnl)
	
	
	async def _process_request(self, cmd: List[str], chnl: discord.Channel):
		'''
		Processes request to get a nd send a cheat sheet.
		Splits response to avoid surpassing maximum length.
		:param cmd: the received command
		:param channel:
		'''
		res = re.sub(COLOR_CODE, '', get_cht(cmd))
		
		# cht.sh [lang] usually results in an explanation on how to install/compile/run from the terminal
		lang = LANG_ALIASES.get(cmd[0], cmd[0]) if len(cmd) > 1 else 'bash'
		max_len = MAX_LEN - len(lang) - 8  # len('```\n\n```')
					
		while res != '\n':
			part = res[:max_len]
			last = part.rfind('\n')
			if last != -1:
				part = part[:last]
			
			res = res[len(part):]
			await self.send_message(chnl, f'```{lang}\n{part}\n```')