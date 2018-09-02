import aiohttp
from typing import List

from consts import *  # pylint: disable=W0614


async def get_cht(cmd: List[str]) -> str:
	'''
	Gets the output from the cht.sh server.
	:param cmd: input for the server
	'''
	# get a response for cmd
	async with aiohttp.get(f"{API_URL_BASE}{cmd[0]}/{'+'.join(cmd[1:])}", headers=CURL_HEADER) as response:
		if response.status >= 500:  # server error
			return SERVER_ERROR
		response.raise_for_status()  # client error, pass to on_error()
		
		return await response.text()


async def check_lang(lang: str) -> str:
	'''
	Finds the language in the language list to make sure it is valid.
	:return: an empty string if valid, or an error message.
	'''
	lines = await get_cht([':list']).splitlines()
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