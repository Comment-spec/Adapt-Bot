def NoneTest(var, new_value):
	if var is None:
		var = new_value
	return var
def FixRow(row, length):
	my_row = []
	i = 0
	for value in row:
		my_row.append(value)
		i += 1
	for i in range(i, length):
		my_row.append('')
	return my_row

class Raiding:
	def __init__(self, *args, **kwargs):
		metadata_dict = NoneTest(kwargs.get('metadata'), {'num_raids': 0, 'types': {}})
		raid_table = NoneTest(kwargs.get('raids'), [{}])
		application_table = NoneTest(kwargs.get('application_lists'), [{}])
		
		self.metadata = metadata_dict
		self.raid_list = []
		for raid_dict in raid_table:
			self.raid_list.append(self.Raid(raid_dict))
		self.application_lists = []
		for application_dict in application_table:
			self.application_lists.append(self.ApplicationList(application_dict))

	class Raid:
		def __init__(self, raid_dict):
			self.number = int(NoneTest(raid_dict.get('number'), 0))
			info_table = NoneTest(raid_dict.get('info_table'), ['', '', '', '', ''])
			roster_table = NoneTest(raid_dict.get('roster_table'), [['', '', '', '', '', '']])

			self.name = info_table[0]
			self.day = info_table[1]
			self.date = info_table[2]
			self.time = info_table[3]
			self.type = info_table[4]
			self.roster = []
			for character_row in roster_table:
				self.roster.append(self.Character(character_row))

		class Character:
			def __init__(self, character_row):
				my_character_row = FixRow(character_row, 6)
				self.name = my_character_row[0]
				self.discord = my_character_row[1]
				self.wow_class = my_character_row[2]
				self.role = my_character_row[3]
				self.soft_res_one = my_character_row[4]
				self.soft_res_two = my_character_row[5]

	class ApplicationList:
		def __init__(self, application_dict):
			self.type = NoneTest(application_dict.get('type'), '')
			self.applicant_table = NoneTest(application_dict.get('applicant_table'), [['', '', '', '', '', '', '', '', '', '', '']])

			self.applicants = []
			for character_row in self.applicant_table:
				self.applicants.append(self.Character(character_row))

		class Character:
			def __init__(self, character_row):
				try:
					self.name = character_row[0]
					self.discord = character_row[1]
					self.wow_class = character_row[2]
					self.role = character_row[3]
					self.soft_res_one = character_row[4]
					self.soft_res_two = character_row[5]
					self.date = character_row[6]
					self.time = character_row[7]
					self.guild = character_row[8]
					self.wcl = character_row[9]

					self.raids = []
					i = 10
					for i in range(i, len(character_row)):
						self.raids.append(character_row[i])
				except:
					self.name = ''
					self.discord = ''
					self.wow_class = ''
					self.role = ''
					self.soft_res_one = ''
					self.soft_res_two = ''
					self.date = ''
					self.time = ''
					self.guild = ''
					self.wcl = ''
					self.raids = ['']