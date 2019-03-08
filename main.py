import logging
import argparse
from logging import log
from os import environ
from sys import exit

from bot import CheatClient


if __name__ == '__main__':
	logging.basicConfig(level=logging.WARN)
	
	token: str
	arg_parser = argparse.ArgumentParser(description='Cheat.sh discord bot!')
	arg_parser.add_argument('--token', action='store', metavar='token', dest='token')
	args = arg_parser.parse_args()
	if args.token:
		token = args.token
		log(logging.INFO, "got token from command line")
	elif 'TOKEN' in environ:
		log(logging.INFO, "got token from ENV")
		token = environ.get('TOKEN')
	else:
		arg_parser.print_help()
		exit(1)
	# run the bot with our token
	CheatClient().run(token)
	print()
