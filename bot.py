import discord
import logging
import re
import traceback

from logging import log, INFO
from typing import Dict, List, Optional, NewType

from util import get_cht, check_lang
from consts import *  # pylint: disable=W0614


ChannelID = NewType('ChannelID', str)


class CheatClient(discord.Client):
	"""Custom discord client for cht.sh commands"""
	
	shells: Dict[ChannelID, str] = {}
	
	async def on_ready(self):
		"""
		Sets presence to a useful message.
		:return: None
		"""
		await self.change_presence(game=discord.Game(name=STATUS))
	
	async def on_server_join(self, server: discord.Server):
		"""
		Client connected, sends a Hi message to general
		:param server: the server the client just joined to
		:return: None
		"""
		log(INFO, f'Successfully logged in to {server.name}')
		
		channel = _default_channel(server)
		if channel:
			await self.send_message(channel, HELP_MSG)
	
	async def on_message(self, message: discord.Message):
		"""
		A message was sent, respond if needed
		:param message: the received message
		:return: None
		"""
		cmd = message.content.split('#')[0].replace(COLON_REPLACE, ':').split()
		if not cmd:
			return
		
		if cmd[0] == CWORD:
			cmd = cmd[1:]
			if not cmd or HELP in cmd:  # show help message
				await self.send_message(message.channel, HELP_MSG)
			
			elif cmd[0] == SHELL:  # activate shell mode
				lang = ''
				if len(cmd) >= 2:
					err = await check_lang(cmd[1])
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
	
	async def on_error(self, event: str, *args, **kwargs):
		"""
		Sends an error message to the user, and the error's traceback to us.
		:param event: name of the method that caused the error
		:return: None
		"""
		info = f'Error in {event}:\n'
		
		# Custom error for each event
		if event == 'on_server_join':
			channel = _default_channel(args[0])
			info += 'Server: {0.name} ({0.id})'.format(args[0])
		elif event == 'on_message':
			channel = args[0].channel
			info += 'Message by {0.author.name}: "{0.content}"'.format(args[0])
		else:
			channel = None
		
		info += f'\n```python\n{traceback.format_exc()}\n```'
		log(logging.ERROR, info)
		await self.send_message(self.get_channel(ERRORS_CHANNEL), info)
		
		if channel:
			await self.send_message(channel, ERROR_MSG)
	
	async def _handle_shell(self, cmd: List[str], chnl: discord.Channel):
		"""
		Handles commands in shell mode.
		:param cmd: the received command
		:param chnl: the channel the command was sent from
		:return: None
		"""
		if cmd[0] == 'help':
			await self.send_message(chnl, HELP_SHELL)
		elif cmd[0] == 'cd':
			if len(cmd) < 2 or cmd[1] == '..':
				self.shells[chnl.id] = ''
			else:
				err = await check_lang(cmd[1])
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
		"""
		Processes request to get a nd send a cheat sheet.
		Splits response to avoid surpassing maximum length.
		:param cmd: the received command
		:param chnl: the channel the command was sent from
		"""
		res = re.sub(COLOR_CODE, '', await get_cht(cmd))
		
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


def _default_channel(s: discord.Server) -> Optional[discord.Channel]:
	"""
	Helper function to find a server's default channel.
	Currently searches for a channel named "general".
	:param s: the server to find the default channel of
	:return: the server's default channel, or None if not found
	"""
	return discord.utils.find(lambda c: c.name == 'general', s.channels)
