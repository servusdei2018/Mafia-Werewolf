"""
OpenMafia/OpenWerewolves
Copyright (C) 2019. All Rights Reserved.

A terminal-based multiplayer Mafia/Werewolf clone with Artificial
Intelligence, roles, turns, and more!
"""

class Player:

	def __init__(self, Name):

		"""
		Initialize this Player object

		:Name: string
		  The name of the player
		"""

		#Validate
		if type(Name) != str:
			raise TypeError('Type mismatch: string expected, got type: %s' % type(Name))

		#Assign
		self.Name = Name
		self.Role = None
		self.IsBot = False
		
	def tombstone(self):
		
		"""
		Generate a tombstone for this player
		
		:self: player, this player object
		:return: string, tombstone
		"""

		return '\r\n'.join(
			[
				' ______________ ',
				'/     R I P    \\',
				'|   Here lies  |',
				'|'+self.Name.center(14)+'|',
				'|              |',
				'|Loyal '+self.Role.center(8)+'|',
				'|______________|',
				
			]
		)
