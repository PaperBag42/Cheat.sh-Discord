import logging
from logging import log, INFO
from os import environ
from sys import argv, exit

from bot import CheatClient


if __name__ == '__main__':
	logging.basicConfig(level=logging.WARN)
	
	if len(argv) > 1:
		token = argv[1]
		log(INFO, f'Got token from command line: {token}')
	elif 'TOKEN' in environ:
		token = environ.get('TOKEN')
		log(INFO, f'Got token from env: {token}')
	else:
		log(INFO, 'Usage: python bot.py TOKEN')
		exit(1)
	
	CheatClient().run(token)