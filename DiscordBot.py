import discord
import asyncio
import discord.ext
import discord.utils
from Controller import Controller

class Bot(discord.Client):
	def __init__(self, dict, controller):
		discord.Client.__init__(self)
		self.controller = controller
		self.info = dict
		self.guild = None
		self.message_channel = None
		self.command_channel = None
		self.error_channel = None
		self.command_list = ['!absent', '!change', '!help', '!commands', '!info', '!raid', '!guild', '!invites', '!advertise', '!raidcheck', '!roleassign', '!pugpurge']

	async def on_ready(self):
		for guild in self.guilds:
			if guild.name == self.info.get('server', ''):
				self.guild = guild
		self.message_channel = discord.utils.get(self.get_all_channels(), guild__name=self.guild.name, name=self.info.get('message_channel', ''))
		self.command_channel = discord.utils.get(self.get_all_channels(), guild__name=self.guild.name, name=self.info.get('command_channel', ''))
		self.error_channel = discord.utils.get(self.get_all_channels(), guild__name=self.guild.name, name=self.info.get('error_channel', ''))
		print('We have logged on.\nUser: {0}\nGuild: {1}\nMessage Channel: {2}\nCommand Channel: {3}\nError Channel: {4}'.format(self.user, self.guild, self.message_channel, self.command_channel, self.error_channel))

	# SIMPLE COMMANDS
	async def message(self, channel, str):
		try:
			await channel.send(str)
		except discord.errors.HTTPException:
			i = 0
			while i < len(str):
				if i+1999 > len(str):
					split_str = str[i:len(str)-1]
				else:
					split_str = str[i:i+1999]
				await channel.send(split_str)
				i += 2000
		except:
			await self.error_channel.send('MESSAGING ERROR:\nSent to:\n`{0}`\n\nMessage content:\n{1}'.format(channel.name, str))

	# ON_MESSAGE
	async def on_message(self, message):
		# CHECKS
		if message.author == self.user:
			return

		if message.guild is not None and message.guild.name != self.guild.name:
			return

		# COMMANDS
		async def absent(message):
			await self.message(self.message_channel, '{0}#{1} is going to be absent from a raid. An Officer should message them.'.format(message.author.name, message.author.discriminator))
			await self.message(message.author, 'Your absence has been recorded. If you are signed up for multiple raids, an Officer will message you.')

		async def change(message):
			await self.message(self.message_channel, '{0}#{1} wants to change their raid time. An Officer should message them.'.format(message.author.name, message.author.discriminator))
			await self.message(message.author, 'Your request has been recorded. If another slot is open, an Officer will message you. If you will 100% be absent from your current raid, please send me **`!absent`**.')

		async def help(message):
			await self.message(message.channel, '**`!raid`** - Apply to join one of our raids.' +
				'\n**`!change`** - Informs us that you wish to change from one raid to another.' +
				'\n**`!absent`** - Informs us that you will be absent from a raid you were invited to.' +
				'\n**`!guild`** - Apply to join the guild, <Adapt>.' +
				'\n**`!raidcheck`** - Check the raids that you are applied to, including your soft reserve items.')

		async def raid(message):
			await self.raid_conversation(message.author)

		async def guild(message):
			await self.guild_conversation(message.author)

		async def invites(message):
			await self.invites_conversation(message.author)

		async def advertise(message):
			await self.advertise_conversation(message.author)

		async def raidcheck(message):
			await self.raidcheck_message(message.author)

		async def help_command_channel():
			await self.message(self.command_channel, '**`!invites`** - Sends a message to everyone that has been added to the roster for one of the raids, letting them know they were invited.' +
				'\n**`!advertise`** - Sends a message to everyone in the discord informing them about the upcoming raids and reminding them to apply.' +
				'\n**`!pugpurge`** - purges all the members from a selected role.' +
				'\n**`!roleassign`** - purges all the members from a selected role.')

		async def pugpurge(message):
			await self.pugurge_conversation(message.author)

		async def roleassign(message):
			await self.roleassign_conversation(message.author)

		# MESSAGES
		if message.content == '!absent':
			await absent(message)

		elif message.content == '!change':
			await change(message)

		elif message.content == '!help' or message.content == '!commands' or message.content == '!info':
			await help(message)

		elif message.content == '!raid':
			await raid(message)

		elif message.content == '!guild':
			await guild(message)

		elif message.content == '!raidcheck':
			await raidcheck(message)

		# COMMAND CHANNEL MESSAGES
		if message.guild is not None and message.channel.name == self.command_channel.name:

			if message.content == '!help' or message.content == '!commands' or message.content == '!info':
				await help_command_channel()

			elif message.content == '!invites':
				await invites(message)

			elif message.content == '!advertise':
				await advertise(message)

			elif message.content == '!pugpurge':
				await pugpurge(message)

			elif message.content == '!roleassign':
				await roleassign(message)

	async def conversation(self, str, channel, check, timeout):
		await self.message(channel, str)
		try:
			response = await self.wait_for('message', timeout=timeout, check=check)
			if response.content in self.command_list:
				await self.message(channel, 'A command is not a valid response. Your old conversation is over.')
				return False, None
			else:
				return True, response
		except asyncio.TimeoutError:
			await self.message(channel, 'This conversation has timed out. Please try again.')
			return False, None

	async def raid_conversation(self, user):
		def check(response):
			return response.channel == user.dm_channel and response.author == user
		def yes_check(response):
			return response.channel == user.dm_channel and (response.content == 'yes' or response.content == 'Yes') and response.author == user

		my_raiding = self.controller.get_raiding()
		application = {}
		num_raids = my_raiding.metadata.get('num_raids', 0)
		application.update({'num_raids': num_raids})
		conversing = True

		try:
			while(conversing):
				await self.message(user, StringMachine.raids_recruitment(my_raiding.raid_list, my_raiding.metadata))

				conversing, type = await self.conversation('Which type would you like to apply for? Please type the name of the type. (ex. CurrentWeek, or NextWeek)', user, check, 120.0)
				if type.content == 'currentweek':
					type.content = 'CurrentWeek'
				if type.content == 'special':
					type.content = 'Special'
				if not self.controller.check_type_exists(type.content):
					await self.message(user, 'That type does not exist! Please try again.')
					return
				else:
					application.update({'type': type.content})

				conversing, response = await self.conversation('You have selected the following:\n\n{0}\n\nIs this correct? Please type "Yes" or "No".'.format(StringMachine.raids_info_for_type(my_raiding.raid_list, my_raiding.metadata, type.content)), user, check, 60.0)
				if response.content == 'yes' or response.content == 'Yes':
					for raid in my_raiding.raid_list:
						if raid.type == type.content:
							conversing, response = await self.conversation('Would you be able to attend the following Raid? Please type "Yes" or "No".\n{0}'.format(StringMachine.raid_info(raid)), user, check, 60.0)
							if response.content == 'yes' or response.content == 'Yes':
								application.update({raid.number: '{0} {1}'.format(raid.date, raid.time)})
				else:
					await self.message(user, 'Your application has been cancelled!')
					return

				i = 1
				signed_up_for_any_raid = False
				for i in range(i, num_raids+1):
					signed_up_for_raid = application.get(i, '')
					if signed_up_for_raid != '':
						signed_up_for_any_raid = True
				if not signed_up_for_any_raid:
					await self.message(user, 'You didn\'t sign up for any raids! Your application has been cancelled!')
					return

				conversing, character_name = await self.conversation('What is the name of your character?', user, check, 60.0)
				application.update({'character_name': character_name.content})
				conversing, character_class = await self.conversation('What is your character\'s class?', user, check, 60.0)
				application.update({'class': character_class.content})
				conversing, character_role = await self.conversation('What is your character\'s role? (DPS, Tank, Healer)', user, check, 60.0)
				application.update({'role': character_role.content})
				conversing, character_guild = await self.conversation('What is the name of the Guild that your character is in?', user, check, 60.0)
				application.update({'guild': character_guild.content})
				conversing, soft_res_one = await self.conversation('What is the first item that you would like to soft reserve?', user, check, 120.0)
				application.update({'soft_res_one': soft_res_one.content})
				conversing, soft_res_two = await self.conversation('What is the second item that you would like to soft reserve?', user, check, 120.0)
				application.update({'soft_res_two': soft_res_two.content})
				application.update({'discord_name': '{0}#{1}'.format(user.name, user.discriminator)})

				self.controller.add_applicant(application)
				await self.message(user, 'Your application has been submitted! ' +
					'If you have additional characters or would like to sign up for an additional week, please apply again with **`!raid`**.')
				return
		except AttributeError:
			await self.message(user, 'Error. Please try again.')

	async def guild_conversation(self, user):
		def check(response):
			return response.channel == user.dm_channel and response.author == user

		conversing = True
		try:
			while conversing:
				await self.message(user, 'Hello! In order to apply to <Adapt>, please answer my questions.')
				conversing, character_name = await self.conversation('What is the name of the character which you intend to join the guild on?', user, check, 60.0)
				conversing, character_class = await self.conversation('What is your character\'s class?', user, check, 60.0)
				conversing, character_role = await self.conversation('What is your character\'s role? (DPS, Tank, Healer)', user, check, 60.0)
				conversing, character_level = await self.conversation('What is your character\'s level?', user, check, 60.0)
				conversing, extra_info = await self.conversation('If you have any additional information you\'d like to share, such as raiding experience, please do so now!', user, check, 300.0)
				await self.message(self.message_channel, 'Discord Name: {0}#{1}\nCharacter: {2.content}\nClass: {3.content}\nRole: {4.content}\nLevel: {5.content}\nAdditional Info: {6.content}'.format(
					user.name, user.discriminator, character_name, character_class, character_role, character_level, extra_info))
				await self.message(user, 'Thank you for applying to join <Adapt>! Your application has been submitted.')
				return
		except AttributeError:
			await self.message(user, 'Error. Please try again.')

	async def invites_conversation(self, user):
		def check(response):
			return response.channel.name == self.command_channel.name and response.author == user
		def digit_check(response):
			return response.channel.name == self.command_channel.name and response.content.isdigit() and response.author == user
		def member_exists(character_name, discord_name, guild):
			member = guild.get_member_named(discord_name)
			if member is None:
				return False
			else:
				return True

		conversing = True
		try:
			while conversing:
				conversing, raid_num = await self.conversation('What is the number of the raid that you wish to send out invites for?', self.command_channel, digit_check, 60.0)

				my_raiding = self.controller.get_raiding()
				my_raid = None
				for raid in my_raiding.raid_list:
					if raid.number == int(raid_num.content):
						my_raid = raid
				if my_raid is None:
					await self.message(self.command_channel, 'That raid does not exist.')
					return

				all_members_exist = True
				erroneous_members_string = ''
				members_string = ''
				for character in my_raid.roster:
					if not member_exists(character.name, character.discord, self.guild):
						all_members_exist = False
						erroneous_members_string += StringMachine.character_info(character) + '\n'
					members_string += StringMachine.character_info(character) + '\n'

				await self.message(self.command_channel, 'The following raid:\n{0}'.format(StringMachine.raid_info(my_raid)))
				await self.message(self.command_channel, 'The following characters:\n{0}'.format(members_string))
				conversing, response = await self.conversation('If this is acceptable, then please type "yes" to confirm.', self.command_channel, check, 60.0)
				if response.content != 'Yes' and response.content != 'yes':
					await self.message(self.command_channel, 'Invites have been cancelled.')
					return

				conversing, response = await self.conversation('Would you like to assign a role to this raid?\nType Yes or No (Or anything else really if you dont want to do it)', self.command_channel, check, 60.0)
				if response.content == 'yes' or response.content == 'Yes':
					conversing, response = await self.conversation('Please select the NUMBER of the following list of roles\n\n	1. MC Sunday Pug\n	2. MC Wednesday Pug\n\n If you no longer wish to assign a role then honestly just type anything else.', self.command_channel, check, 60.0)
					if response.content == '1':
						rolename = 'MC Sunday Pug'
						if all_members_exist:
							for character in my_raid.roster:
								user = self.guild.get_member_named(character.discord)
								await user.add_roles(discord.utils.get(user.guild.roles, name=rolename))
							await self.message(self.command_channel, 'Role assigned\n')
					elif response.content == '2':
						rolename = 'MC Wednesday Pug'
						if all_members_exist:
							for character in my_raid.roster:
								user = self.guild.get_member_named(character.discord)
								await user.add_roles(discord.utils.get(user.guild.roles, name=rolename))
							await self.message(self.command_channel, 'Role assigned\n')

				if all_members_exist:
					for character in my_raid.roster:
						user = self.guild.get_member_named(character.discord)
						await self.message(user, 'Your Character:\n{0}\n\nHas been invited to:\n{1}'.format(StringMachine.character_info(character), StringMachine.raid_info(my_raid)) +
							'\n\nIf you are unable to go to the raid, please respond with **`!absent`**.' +
							'\nIf you are unable to go to the raid you were invited to, but can make another raid time, please respond with **`!change`**.' +
							'\nPlease keep in mind that if you respond with **`!change`**, you are not guaranteed to be invited.')
						await self.message(self.command_channel, 'Message successfully sent to: {0}\n'.format(StringMachine.character_info(character)))
					return

				else:
					await self.message(self.command_channel, 'The following members from the roster are either not part of the discord server or have their discord names spelled incorrectly:\n{0}'.format(erroneous_members_string))
					return
		except AttributeError:
			await self.message(user, 'Error. Please try again.')

	async def advertise_conversation(self, user):
		def check(response):
			return response.channel.name == self.command_channel.name and response.author == user
		
		my_raid_list = self.controller.get_raid_list()
		my_metadata = self.controller.get_metadata()
		conversing = True
		try:
			while conversing:
				conversing, response = await self.conversation('Raiders will be invited to join the following:\n\n{0}\n\nIf this is acceptable, then please type "yes" to confirm.'.format(StringMachine.raids_recruitment(my_raid_list, my_metadata)),
					self.command_channel, check, 60.0)

				if response.content == 'yes' or response.content == 'Yes':
					members_list = self.guild.members
					for user in members_list:
						try:
							if not user.bot:
								await self.message(user, '{0}\n\nIf you would like to apply to raid with us, then please message me with **`!raid`**.'.format(StringMachine.raids_recruitment(my_raid_list, my_metadata)))
								await self.message(self.command_channel, 'Advertisement sent to: {0}#{1}'.format(user.name, user.discriminator))
						except:
							pass
					return

				else:
					await self.message(self.command_channel, 'Advertisements have been cancelled.')
					return
		except AttributeError:
			await self.message(user, 'Error. Please try again.')

	async def raidcheck_message(self, user):
		my_raiding = self.controller.get_raiding()
		str = 'You have applied for the following raids:'

		for application_list in my_raiding.application_lists:
			for character in application_list.applicants:
				if character.discord == '{0}#{1}'.format(user.name, user.discriminator):
					str += '\n\n{0}'.format(StringMachine.raids_info_for_type(my_raiding.raid_list, my_raiding.metadata, application_list.type))
					for character in application_list.applicants:
						if character.discord == '{0}#{1}'.format(user.name, user.discriminator):
							str += '\n\nThe Character:\n{0}'.format(StringMachine.character_info(character))
							str += '\n\nIs applied for:\n{0}'.format(StringMachine.applicant_raid_info(character))
					break

		if str == 'You have applied for the following raids:':
			await self.message(user, 'You have not applied for any of our raids!')
			return

		await self.message(user, str)
		return

	async def pugurge_conversation(self, user):
		def check(response):
			return response.channel.name == self.command_channel.name and response.author == user
		members_list = self.guild.members
		conversing = True
		try:
			while conversing:
				conversing, response = await self.conversation('Please select the NUMBER of the following list of roles you wish to remove the members of\n\n1. MC Sunday Pug\n2. MC Wednesday Pug\n3. Green Team\n\nIf you no longer wish to purge a role then honestly just type anything else.', self.command_channel, check, 60.0)
				if response.content == '1':
					role = discord.utils.get(user.guild.roles, name='MC Sunday Pug')
					for member in members_list:
						if role in member.roles:
							await member.remove_roles(role)
					await self.message(self.command_channel, 'All member from this role have been removed.')
					return
				elif response.content == '2':
					role = discord.utils.get(user.guild.roles, name='MC Wednesday Pug')
					for member in members_list:
						if role in member.roles:
							await member.remove_roles(role)
					await self.message(self.command_channel, 'All member from this role have been removed.')
					return
				elif response.content == '3':
					role = discord.utils.get(user.guild.roles, name='Green Team')
					for member in members_list:
						if role in member.roles:
							await member.remove_roles(role)
					await self.message(self.command_channel, 'All member from this role have been removed.')
					return
				else:
					await self.message(self.command_channel, 'Nevermind then.')
				return
		except AttributeError:
			await self.message(user, 'Error. Please try again.')

	async def roleassign_conversation(self, user):
		def check(response):
			return response.channel.name == self.command_channel.name and response.author == user
		def digit_check(response):
			return response.channel.name == self.command_channel.name and response.content.isdigit() and response.author == user
		def member_exists(character_name, discord_name, guild):
			member = guild.get_member_named(discord_name)
			if member is None:
				return False
			else:
				return True

		conversing = True
		try:
			while conversing:
				conversing, raid_num = await self.conversation('What is the number of the raid that you wish to assign a role to?', self.command_channel, digit_check, 60.0)
				my_raiding = self.controller.get_raiding()
				my_raid = None
				for raid in my_raiding.raid_list:
					if raid.number == int(raid_num.content):
						my_raid = raid
				if my_raid is None:
					await self.message(self.command_channel, 'That raid does not exist.')
					return

				all_members_exist = True
				erroneous_members_string = ''
				members_string = ''
				for character in my_raid.roster:
					if not member_exists(character.name, character.discord, self.guild):
						all_members_exist = False
						erroneous_members_string += StringMachine.character_info(character) + '\n'
					members_string += StringMachine.character_info(character) + '\n'

				await self.message(self.command_channel, 'The following raid:\n{0}'.format(StringMachine.raid_info(my_raid)))
				await self.message(self.command_channel, 'The following characters:\n{0}'.format(members_string))
				conversing, response = await self.conversation('If this is acceptable, then please type "yes" to confirm.', self.command_channel, check, 60.0)
				if response.content != 'Yes' and response.content != 'yes':
					await self.message(self.command_channel, 'Raid assignment has been cancelled.')
					return
				conversing, response = await self.conversation('Please select the NUMBER of the following list of roles\n\n1. MC Sunday Pug\n2. MC Wednesday Pug\n3. Green Team\n\n If you no longer wish to assign a role then honestly just type anything else.', self.command_channel, check, 60.0)
				if response.content == '1':
					rolename = 'MC Sunday Pug'
					if all_members_exist:
						for character in my_raid.roster:
							user = self.guild.get_member_named(character.discord)
							await user.add_roles(discord.utils.get(user.guild.roles, name=rolename))
					await self.message(self.command_channel, 'Role assigned\n')
					return
				elif response.content == '2':
					rolename = 'MC Wednesday Pug'
					if all_members_exist:
						for character in my_raid.roster:
							user = self.guild.get_member_named(character.discord)
							await user.add_roles(discord.utils.get(user.guild.roles, name=rolename))
					await self.message(self.command_channel, 'Role assigned\n')
					return
				elif response.content == '3':
					rolename = 'Green Team'
					if all_members_exist:
						for character in my_raid.roster:
							user = self.guild.get_member_named(character.discord)
							await user.add_roles(discord.utils.get(user.guild.roles, name=rolename))
					await self.message(self.command_channel, 'Role assigned\n')
					return
				else:
					await self.message(self.command_channel, 'The following members from the roster are either not part of the discord server or have their discord names spelled incorrectly:\n{0}'.format(erroneous_members_string))
					return
		except AttributeError:
			await self.message(user, 'Error. Please try again.')

class StringMachine:
	def raid_info(raid):
		str = '`{0} - {1} - {2} - {3}`'.format(raid.name, raid.day, raid.date, raid.time)
		return str

	def raids_info_for_type(raid_list, metadata, type):
		str = 'For Type: **`{0}`**:\n***`{1}`***'.format(type, metadata.get('types', {}).get(type, ''))
		i = 0
		num_raids = metadata.get('num_raids', 0)
		while i < num_raids:
			for raid in raid_list:
				if raid.type == type:
					str += '\n{0}'.format(StringMachine.raid_info(raid))
				i += 1
		return str

	def raids_info(raid_list, metadata):
		str = ''
		for type_key in metadata.get('types').keys():
			str += StringMachine.raids_info_for_type(raid_list, metadata, type_key) + '\n\n'
		# Remove last \n
		if str != '':
			str = str[:-2]
		return str

	def raids_recruitment(raid_list, metadata):
		str = 'Hello!\n<Adapt> is hosting the following Raids:\n{0}'.format(StringMachine.raids_info(raid_list, metadata))
		return str

	def character_info(character):
		str = 'Name: `{0}` - Discord: `{1}` - Class: `{2}` - Role: `{3}` - Soft Res One: `{4}` - Soft Res Two: `{5}`'.format(character.name, character.discord, character.wow_class, character.role, character.soft_res_one, character.soft_res_two)
		return str

	def applicant_raid_info(character):
		str = ''
		for raid in character.raids:
			if raid != '':
				str += '`{0}`\n'.format(raid)
		if str != '':
			str = str[:-1]
		return str