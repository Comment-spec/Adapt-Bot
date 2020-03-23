from datetime import datetime
from Sheet import Sheet
from Raiding import Raiding

class Controller:
	## In: {scope: [], id: '', ranges: {}}
	# ranges: {types: '', num_raids: '', info: '', roster: ''}
	def __init__(self, dict):
		self.sheet_controller = self.SheetController(dict.get('scope', None), dict.get('id', None), dict.get('ranges', None))
		self.raiding_controller = self.RaidingController()

	# In: {num_raids: 0, type: '', character_name: '', discord_name: '', class: '', role: '', soft_res_one: '', soft_res_two: '', guild: '', N: '', N+1: '', N+n: ''}
	def add_applicant(self, app_dict):
		application = []
		application.append(app_dict.get('character_name', ''))
		application.append(app_dict.get('discord_name', ''))
		application.append(app_dict.get('class', ''))
		application.append(app_dict.get('role', ''))
		application.append(app_dict.get('soft_res_one', ''))
		application.append(app_dict.get('soft_res_two', ''))
		now = datetime.now()
		application.append(now.strftime('%m-%d-%y'))
		application.append(now.strftime('%I:%M %p'))
		application.append(app_dict.get('guild'))
		application.append('https://classic.warcraftlogs.com/character/us/herod/{0}'.format(app_dict.get('character_name'), ''))

		num_raids = app_dict.get('num_raids', 0)
		for i in range(1, num_raids+1):
			str = app_dict.get(i, '')
			application.append(str)

		app_type = app_dict.get('type', '')
		self.sheet_controller.write_application(app_type, application)

	def get_metadata(self):
		metadata = self.sheet_controller.read_metadata()
		return metadata	

	def get_raid(self, raid_num):
		raid_dict = self.sheet_controller.read_raid(raid_num)
		raid = self.raiding_controller.create_raid(raid_dict)
		return raid

	def get_raid_list(self):
		raid_table = self.sheet_controller.read_raid_list()
		raid_list = self.raiding_controller.create_raid_list(raid_table)
		return raid_list

	def get_application_list(self, type):
		application_dict = self.sheet_controller.read_application_list(type)
		application_list = self.raiding_controller.create_application_list(application_dict)
		return application_list

	def get_application_lists(self):
		application_table = self.sheet_controller.read_application_lists()
		application_lists = self.raiding_controller.create_application_lists(application_table)
		return application_lists

	def get_raiding(self):
		metadata, raid_table, application_table = self.sheet_controller.read_everything()
		raiding = self.raiding_controller.create_raiding(metadata, raid_table, application_table)
		return raiding

	def check_type_exists(self, type):
		try:
			tmp = self.sheet_controller.read_application_list(type)
			return True
		except:
			return False

	class SheetController:
		def __init__(self, scope, id, ranges):
			self.sheet = Sheet(scope, id)
			self.ranges = ranges

		## READ
		# Returns Dict
		def read_metadata(self):
			data = self.sheet.fetch(self.ranges.get('num_raids', None))
			num_raids = int(data[0][0])
			data = self.sheet.fetch(self.ranges.get('types', None))
			types = {}
			for row in data:
				types.update({row[0]: row[1]})
			metadata = {'num_raids': num_raids, 'types': types}
			return metadata

		# Returns 1D Array
		def read_info(self, raid_num):
			data = self.sheet.fetch(self.ranges.get('info', None) % raid_num)
			info = data[0]
			return info

		# Returns 2D Array
		def read_roster(self, raid_num):
			data = self.sheet.fetch(self.ranges.get('roster', None) % raid_num)
			roster = data
			return roster

		# Returns Dict
		def read_raid(self, raid_num):
			raid = {'number': raid_num, 'info_table': self.read_info(raid_num), 'roster_table': self.read_roster(raid_num)}
			return raid

		# Returns List
		def read_raid_list(self):
			metadata = self.read_metadata()
			raid_list = []
			for i in range(1, int(metadata.get('num_raids', None))+1):
				raid = self.read_raid(i)
				raid_list.append(raid)
			return raid_list

		# Returns Dict
		def read_application_list(self, type):
			data = self.sheet.fetch('{0}Applications'.format(type))
			data.pop(0)
			application_list = {'type': type, 'applicant_table': data}
			return application_list

		# Returns List
		def read_application_lists(self):
			metadata = self.read_metadata()
			types = metadata.get('types', {})
			application_lists = []
			for key in types.keys():
				application_list = self.read_application_list(key)
				application_lists.append(application_list)
			return application_lists

		# Returns tuple
		def read_everything(self):
			metadata = self.read_metadata()
			raid_list = self.read_raid_list()
			application_lists = self.read_application_lists()
			return metadata, raid_list, application_lists

		## WRITE
		def write_row(self, range, row):
			body = {'values': [row]}
			self.sheet.append(range, body)

		def write_application(self, type, application):
			self.write_row('{0}Applications'.format(type), application)

	class RaidingController:
		# Returns Object
		def create_raiding(self, metadata_dict, raid_table, application_lists):
			return Raiding(metadata=metadata_dict, raids=raid_table, application_lists=application_lists)

		# Returns List
		def create_raid_list(self, raid_table):
			return Raiding(raids=raid_table).raid_list

		# Returns Object
		def create_raid(self, raid_dict):
			return Raiding(raids=[raid_dict]).raid_list[0]

		# Returns List
		def create_application_lists(self, application_lists):
			return Raiding(application_lists=application_lists).application_lists

		# Returns Object
		def create_application_list(self, application_dict):
			return Raiding(application_lists=[application_dict]).application_lists[0]