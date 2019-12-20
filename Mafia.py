"""
OpenMafia/OpenWerewolves
Copyright (C) 2019. All Rights Reserved.

A terminal-based multiplayer Mafia/Werewolf clone with Artificial
Intelligence, roles, turns, and more!

There are 7 players: 3 mafia, 1 doctor, 1 police, and 2 citizens.
Roles are randomly assigned, and as many as 7 humans may play,
with a minimum of one.

There are no requirements aside from the standard library.
"""

from random import sample, randint
from player import Player

__version__ = 1.00

#SETTINGS
tombstone=False # Whether to display a tombstone after the death of a player, showing his role
do_colorize=True # Whether to display ANSI color codes
#END SETTINGS

players = []
to_lynch = []
to_heal = []
to_assassinate = []

assanTaken=False
currentRound = 'day'

def main():

	"""
	Main application entrypoint
	"""

	global players

	print('OpenMafia')
	print('v%s' % __version__)
	print()

	stop=False
	while not stop:
		stop=addPlayer()

	if len(players) < 1:
		raise RuntimeError('Must have at least one player.')

	assignRoles()

	for p in players:
		print('Player Name: %s, Role: %s, IsBot: %s' % (p.Name, p.Role, p.IsBot))

	stop=False
	while not stop:
		newRound()

def newRound():

	"""
	One round of actions (each player takes a turn)
	"""

	global players, currentRound, assanTaken
	global to_assassinate, to_heal, to_lynch

	assanTaken=False
	to_assassinate=[]
	to_heal=[]
	to_lynch=[]

	for player in players:
		playerTurn(player)

	print()
	input('End Of Round!')

	print()

	for name in to_assassinate:
		if name in to_heal:
			print('Someone tries to assassinate %s, but the doctor saves him!' % name)
		else:
			msgs=[
				'%s has been found dead in a trashcan!',
				'%s has been found dead, stabbed in the heart!',
				'%s has been viciously murdered!'
			]
			print(str('\033[1;31m'+sample(msgs, 1)[0]+'\033[0m') % name)
			fp=findPlayer(name)
			print()
			if tombstone:
				print(fp.tombstone())
			print()
			cnt=0
			for p in players:
				if p==fp:
					break
				cnt+=1
			del(players[cnt])
		input()

	lynchd={}

	for name in to_lynch:
		fp=findPlayer(name)

		if fp == None:
			continue

		for p in players:
			if p != fp:
				if p.IsBot:
					if randint(0, 3) == 3:
						print('%s votes yes!' % p.Name)
						if fp.Name not in lynchd:
							lynchd[fp.Name] = 0
						lynchd[fp.Name] += 1
					continue
				y=input('%s, vote to lynch %s? [y/n]' % (p.Name, fp.Name))
				if y.lower() == 'y':
					print('%s votes yes!' % p.Name)
					if fp.Name not in lynchd:
						lynchd[fp.Name] = 0
					lynchd[fp.Name] += 1

	for name in lynchd:
		if lynchd[name] >= 3:
			print('\033[1;31m%s has been lynched!\033[0m' % name)
			if tombstone:
				print(findPlayer(name).tombstone())
			input()
			cnt=0
			for p in players:
				if p.Name == name:
					break
				cnt+=1
			del(players[cnt])
		input()

	print()
	print()

	victoryCheck()

	if currentRound == 'day':
		currentRound = 'night'
	else:
		currentRound = 'day'

def victoryCheck():

	"""
	Perform a victory check
	"""

	totals = {
		'Mafia': 0,
		'Police': 0,
		'Doctor': 0,
		'Citizen': 0
	}

	for p in players:
		totals[p.Role] += 1

	if totals['Mafia'] <= 0:
		print()
		print('---->>> The Mafia LOSE! <<<---')
		exit()
	elif totals['Police']==0 and totals['Doctor']==0 and totals['Citizen']==0:
		print()
		print('---->>> The Mafia WIN! <<<---')
		exit()

def playerTurn(player):

	"""
	Enable a player to take his turn

	:player: player, this player
	"""

	if player.IsBot:
		handleBot(player)
		return

	for i in range(0, 100):
		print()

	input("Player {}'s turn! Press <ENTER> to begin ...".format(player.Name))

	print()
	print('You are a %s. It is %s.' % (colorize(player.Role), colorize(currentRound)))

	# Display a list of players
	print('Players: %s' % ', '.join(listOfPlayers()))

	# Display list of available commands
	commandList = availableCommands(player)
	print('Commands: %s' % ', '.join(commandList))

	stopInterpreting=False
	while not stopInterpreting:
		stopInterpreting=interpret(player, commandList)
		if not stopInterpreting:
			print('Invalid command.')

	for i in range(0, 100):
		print()

def colorize(str):

	"""
	Use ASCII color codes to brighten up a role or day/night

	:str: string
	:return: string
	"""

	global do_colorize

	if not do_colorize:
		return str

	if str == 'Police':
		return '\033[1;34mPolice\033[0m'
	if str == 'Mafia':
		return '\033[1;31mMafia\033[0m'
	if str == 'Doctor':
		return '\033[1;33mDoctor\033[0m'
	if str == 'Citizen':
		return '\033[1;32mCitizen\033[0m'
	if str == 'day':
		return '\033[1;38mday\033[0m'
	if str == 'night':
		return '\033[1;34mnight\033[0m'

def handleBot(bot):

	"""
	Handle this bot's turn

	:bot: player, this bot
	"""

	randomPlayer = sample(players, 1)[0]

	if bot.Role == 'Mafia' and currentRound == 'night':
		if randint(0, 3) == 3:
			return

		if randomPlayer == bot: # Nobody assassinates themselves. Ever.
			while randomPlayer == bot:
				randomPlayer = sample(players, 1)[0]

		handler_assassinate('assassinate %s' % randomPlayer.Name)
	if bot.Role == 'Doctor' and currentRound == 'night':
		handler_heal('heal %s' % randomPlayer.Name)
	if currentRound == 'day':
		if randint(0, 3) == 3:
			interpret(bot, 'nominate {}'.format(randomPlayer.Name))

def findPlayer(name):

	"""
	Return player object based on name

	:name: string, name of player
	:return: player object
	"""

	global players

	if name not in listOfPlayers():
		# This might happen if someone has been assassinated before they are lynched.
		return None

	for p in players:
		if p.Name == name:
			return p

def interpret(player, commandList):

	"""
	Interpret a player's command

	:player: player, the current player
	:commandList: dict
	:return: bool, whether or not the player has taken an action
	"""

	cmd=input()

	if cmd=='':
		return False

	kw = cmd.split()[0]

	if kw not in commandList:
		return False

	return commandList[kw](cmd)

def handler_assassinate(cmd):

	"""
	Assassinate a player (MAFIA)

	:cmd: stirng, command
	:return: bool, whether the command is valid
	"""

	global to_assassinate, assanTaken

	if assanTaken == True:
		print('Someone has already chosen a target.')
		input()
		return True

	kwargs=cmd.split()

	if len(kwargs) != 2:
		return False

	name=kwargs[1]

	if name not in listOfPlayers():
		return False

	if name not in to_assassinate:
		to_assassinate.append(name)

	assanTaken=True
	return True

def handler_heal(cmd):

	"""
	Heal a player to make him immune to assassination (DOCTOR)

	:cmd: stirng, command
	:return: bool, whether the command is valid
	"""

	global to_heal

	kwargs=cmd.split()

	if len(kwargs) != 2:
		return False

	name=kwargs[1]

	if name not in listOfPlayers():
		return False

	to_heal.append(name)

	return True

def handler_nominate(cmd):

	"""
	Nominate a player for lynching (EVERYONE)

	:cmd: string, command
	:return: bool, whether the command is valid
	"""

	global to_lynch

	kwargs=cmd.split()

	if len(kwargs) != 2:
		return False

	name=kwargs[1]

	if name not in listOfPlayers():
		return False

	to_lynch.append(name)

	return True

def handler_sleep(cmd):

	"""
	Do nothing (EVERYONE)
	"""

	return True

def handler_investigate(cmd):

	"""
	Investigate a player to find out his role (POLICE)

	:cmd: string, command
	:return: bool, whether the command is valid
	"""

	kwargs=cmd.split()

	if len(kwargs) != 2:
		return False

	name=kwargs[1]

	if name not in listOfPlayers():
		return False

	fp=findPlayer(name)

	print('You investigate %s and find that he is a loyal %s!' % (fp.Name, fp.Role))
	input()

	return True

def availableCommands(p):

	"""
	Return a dictionary of available commands, pointing to handler
	functions.

	:p: player, the current player
	:return: dictionary, available commands -> handler function
	"""

	ret={}

	if currentRound == 'day':

		ret['nominate'] = handler_nominate

	else:

		if p.Role == 'Police':
			ret['investigate'] = handler_investigate
		if p.Role == 'Doctor':
			ret['heal'] = handler_heal
		if p.Role == 'Mafia':
			ret['assassinate'] = handler_assassinate

	if currentRound == 'night':

		ret['sleep'] = handler_sleep

	else:

		ret['wait'] = handler_sleep

	return ret

def listOfPlayers():

	"""
	Return a list of players' names

	:return: string[], list of players' names
	"""

	ret=[]

	for p in players:

		ret.append(p.Name)

	return ret

def addPlayer():

	"""
	Attempt to add a new player

	:return: bool, whether to stop adding new players
	"""

	global players

	name=input('Enter player name (F to finish): ')

	if name.lower()=='f':
		return True

	players.append(Player(name))

	return False

def assignRoles():

	"""
	Assign roles to all players
	"""

	global players

	possibleRoles = ['Mafia', 'Doctor', 'Police', 'Citizen']
	amountOfRoles = {
		'Mafia': [0, 2], #'role': [playersWhoAreThis, playersNeeded]
		'Doctor': [0, 1],
		'Police': [0, 1],
		'Citizen': [0, 3]
	}
	botNames = [
		'Adam',
		'Andrew',
		'Matthew',
		'Nick',
		'Paul',
		'Ryan'
	]

	#Make sure there are 7 players

	if len(players) < 7:

		nameCounter=0

		for i in range(len(players), 7):

			newBot = Player(botNames[nameCounter])
			newBot.IsBot=True
			players.append(newBot)
			nameCounter+=1

	#Then assign roles to players

	for player in players:

			possibles=[]

			for amnt in amountOfRoles:
				if amountOfRoles[amnt][0] < amountOfRoles[amnt][1]:
					possibles.append(amnt)

			selected = sample(possibles, 1)[0]
			player.Role = selected

			amountOfRoles[selected][0] += 1

if __name__ == '__main__':
	main()
