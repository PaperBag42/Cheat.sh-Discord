import logging
import argparse
from logging import log, INFO
from os import environ
from sys import argv, exit

from bot import CheatClient


if __name__ == '__main__':
	logging.basicConfig(level=logging.WARN)
	
	token: str
	arg_parser = argparse.ArgumentParser(description='Cheat.sh discord bot!')
	arg_parser.add_argument('--token', action='store', metavar='token', dest='token')
	args = arg_parser.parse_args()
	if args.token:
		token = args.token
	if 'TOKEN' in environ:
		token = environ.get('TOKEN')
	else:
		arg_parser.print_help()
		exit(1)
		
	CheatClient().run(token)
	print()
