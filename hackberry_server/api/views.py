from api.models import Vocabulary, ActiveGames, Player, PlayedWords
import codecs
import os
from django.http import HttpResponse
import time
import re
from django.utils import simplejson
from random import *

WHITE_NUMBER = '3'
PLAYERA_LIGHTNUMBER = '1'
PLAYERA_DARKNUMBER = '2'
PLAYERB_LIGHTNUMBER = '4'
PLAYERB_DARKNUMBER = '5'
INVALIDWORD_EXCEPTION = "Invalid_Word"
INVALIDWORD_EXCEPTION_PLAYED = "Word_Played"
PLAYERA_SYMBOL = 'A'
PLAYERB_SYMBOL = 'B'

#algorithm 
def neighbors(colorStatus, i):
	nbs = []
	if i > 4:
		nbs.append(i-5)
	if i < 20:
		nbs.append(i+5)
	if i%5 != 0:
		nbs.append(i-1)
	if (i+1)%5 != 0:
		nbs.append(i+1)
	return nbs
		
def upNeiborsMarked(map, i):
	nbs = []
	if i > 4 and map[i-5] >= 0:
		nbs.append(i-5)
	if i%5 != 0 and map[i-1] >= 0:
		nbs.append(i-1)
	return nbs
	
def calculateScoreMap(map, bonus, penalty):
	map = list(map)
	for i in range(25):
		if map[i] == penalty:
			map[i] = -2
			continue
		elif map[i] != bonus:
			map[i] = -1
			continue
		else:
			map[i] = i
		
		nbs = upNeiborsMarked(map, i)
		
		if len(nbs) == 0:
			continue
		if len(nbs) == 2 and map[nbs[0]] != map[nbs[1]]:
			for j in range(i):
				if map[j] == map[nbs[1]]:
					map[j] = map[nbs[0]]
		map[i] = map[nbs[0]]
	return map

def calculateScoreDict(map):
	scoreDict = {}
	for i in range(25):
		if scoreDict.has_key(map[i]):
			scoreDict[map[i]] += 1
		else:
			scoreDict[map[i]]  = 1
	scoreDict[-2] = 0
	scoreDict[-1] = 1
	return scoreDict
#end algorithm

def setPreColorStatus(colorStatus, symbol, move):
	if symbol == 'A':
		for i in range(len(move)):
			color = colorStatus[move[i]]
			if color == WHITE_NUMBER or color == PLAYERB_LIGHTNUMBER:
				colorStatus[move[i]] = PLAYERA_LIGHTNUMBER
	else:
		for i in range(len(move)):
			color = colorStatus[move[i]]
			if color == WHITE_NUMBER or color == PLAYERA_LIGHTNUMBER:
				colorStatus[move[i]] = PLAYERB_LIGHTNUMBER
	return colorStatus

def updateColorStatus(preColorStatus, symbol):
	for i in range(25):
		neighborIndexes = neighbors(preColorStatus, i)
		flag = True
		if symbol == 'A':
			for neighborIndex in neighborIndexes:
				if preColorStatus[neighborIndex] != PLAYERA_LIGHTNUMBER and preColorStatus[neighborIndex] != PLAYERA_DARKNUMBER:
					flag = False
					break;
			if flag:
				preColorStatus[i] = PLAYERA_DARKNUMBER
		else:
			for neighborIndex in neighborIndexes:
				if preColorStatus[neighborIndex] != PLAYERB_LIGHTNUMBER and preColorStatus[neighborIndex] != PLAYERB_DARKNUMBER:
					flag = False
					break;
			if flag:
				preColorStatus[i] = PLAYERB_DARKNUMBER
	colorStatus = "".join(preColorStatus)
	return colorStatus	
					
def importData(request):
	fo = codecs.open("word_resource/chinese_words.txt", 'r', 'gb18030')
	attrStr = fo.readline()
	now = time.time()
	while(True):
		lineStr = fo.readline()
		components = lineStr.strip().split('\t')
		if(len(components) != 3):
			break
		soundWithoutTone = re.sub(ur'''[1234']''', ur'''''', components[1])
		v = Vocabulary(word = components[0], sound = soundWithoutTone, freq = int(components[2]))
		v.save()
	later = time.time()
	difference = int(later - now)
	return HttpResponse("Import Data Complete." + " " + str(difference))
	
def checkSound(request, playerGuess):
	results = Vocabulary.objects.filter(sound = playerGuess)
	to_json = {}
	if len(results) == 0:
		to_json['valid'] = False
	else:
		to_json['valid'] = True	
		words = {}
		for result in results:
			words[result.id] = result.word 		
		to_json['words'] = words
	return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

def generateLetters():
	letters = ""
	for i in range(25) :
		letters += chr(97+randint(0,25))
	return letters
	
def generateGameJSON(game):
	to_json = {}
	to_json['gameID'] = game.id
	to_json['letters'] = game.letters
	to_json['colorStatus'] = game.colorStatus
	to_json['playerA'] = game.playerA
	to_json['playerB'] = game.playerB
	to_json['isTurnA'] = game.isTurnA
	to_json['needOpponent'] = game.needOpponent
	to_json['scoreA'] = game.scoreA
	to_json['scoreB'] = game.scoreB
	to_json['lastPlayedWord'] = game.lastPlayedWord
	return to_json

def generateCommitResponseJSON(words):
	to_json = {}
	if len(words) == 0:
		to_json['valid'] = False
	else:
		to_json['valid'] = True	
		wordsDic = {}
		for word in words:
			wordsDic[word.id] = word.word		
		to_json['words'] = wordsDic
	return to_json

def generateNewGame(playerID, opponentID=0):
	game = ActiveGames()
	game.letters = generateLetters()
	game.colorStatus = "3535415554122533355533333"
	game.playerA = int(playerID)
	game.playerB = int(opponentID)
	game.isTurnA = True
	game.needOpponent = True
	game.scoreA = 0
	game.scoreB = 0
	game.lastPlayedWord = ""
	return game
	
def requestNewGame(request, playerID):
	games = ActiveGames.objects.filter(needOpponent = True).filter(isTurnA = False).exclude(playerA = playerID)
	if len(games) == 0 :
		game = generateNewGame(playerID)
	else:
		games = list(games)
		shuffle(games)
		game = games[0]
		game.playerB = int(playerID)
		game.needOpponent = False
	game.save()
	return HttpResponse(simplejson.dumps(generateGameJSON(game)), mimetype='application/json')

def requestNewGameWithOpponentSpecified(request, playerID, opponentID):
	game = generateNewGame(playerID, opponentID)
	game.needOpponent = False
	game.save()
	return HttpResponse(simplejson.dumps(generateGameJSON(game)), mimetype='application/json')

def matchedWords(move):
	words = Vocabulary.objects.filter(sound = move)
	return words

def calculateScore(game, move, symbol):
	if symbol == 'A':
		connectedRegions = calculateScoreMap(game.colorStatus, PLAYERA_DARKNUMBER, PLAYERB_DARKNUMBER)
	elif symbol == 'B':
		connectedRegions = calculateScoreMap(game.colorStatus, PLAYERB_DARKNUMBER, PLAYERA_DARKNUMBER)
	scoreDict = calculateScoreDict(connectedRegions)
	score = 0
	for i in range(len(move)):
		score += scoreDict[connectedRegions[move[i]]]
	return score

def hasPlayed(gameID, moveWord):
	playedWords = PlayedWords.objects.filter(game = gameID)
	for playedWord in playedWords:
		if playedWord == moveWord:
			return True
	return False

def commit(request, playerID, gameID, move):
	#TODO: check isTurn
	gameID = int(gameID)
	playerID = int(playerID)
	
	game = ActiveGames.objects.filter(id = gameID)
	gameList = list(game)
	game = gameList[0]
	
	move = move.split('_')
	moveWord = ""
	for i in range(len(move)):
		move[i] = int(move[i])
		moveWord += game.letters[move[i]]
	words = matchedWords(moveWord)
	
	"""
	if len(words) == 0:
		to_json = {"Exception": INVALIDWORD_EXCEPTION}
		return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
	if hasPlayed(gameID, moveWord):
		to_json = {"Exception": INVALIDWORD_EXCEPTION_PLAYED}
		return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
	"""
	if game.isTurnA :
		#player is playerA
		if playerID != game.playerA:
			raise Exception(str(type(playerID)) + " " +str(type(game.playerA)))
			raise Exception("It is not playerA's turn.")
		game.scoreA += calculateScore(game, move, 'A')
		game.colorStatus = updateColorStatus(setPreColorStatus(list(game.colorStatus), 'A', move), 'A')
	else:
		if playerID != game.playerB:
			raise Exception("It is not playerB's turn.")
		game.scoreB += calculateScore(game, move, 'B')
		game.colorStatus = updateColorStatus(setPreColorStatus(list(game.colorStatus), 'B', move), 'B')
		
	game.isTurnA = not game.isTurnA
	game.lastPlayedWord = moveWord
	game.save()
	return HttpResponse(simplejson.dumps(generateGameJSON(game)), mimetype='application/json')
			