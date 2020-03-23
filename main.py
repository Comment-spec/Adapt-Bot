from Controller import Controller
from DiscordBot import Bot
import yaml

CONFIG_FILE = 'AdaptBot.yml'

with open(CONFIG_FILE, 'r') as config_file:
	config = yaml.full_load(config_file)

my_controller = Controller(config.get('controller'))
my_client = Bot(config.get('discord'), my_controller)
my_client.run(config.get('bot_id'))