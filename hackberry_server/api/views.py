from api.models import Vocabulary, ActiveGames, Player, PlayedWords
import codecs
import os
from django.http import HttpResponse
import time
import re
from django.utils import simplejson
from random import *

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

def requestNewGame(request, playerID):
	games = ActiveGames.objects.filter(needOpponent = True).filter(isTurnA = False)
	if len(games) == 0 :
		game = ActiveGames()
		game.letters = generateLetters()
		game.colorStatus = "333333333333333333333333333333"
		game.playerA = playerID
		game.playerB = 0
		game.isTurnA = True
		game.needOpponent = True
	else:
		game = shuffle(games)[0]
		game.playerB = playerID
	
	to_json = {}
	to_json['letters'] = game.letters
	to_json['colorStatus'] = game.colorStatus
	to_json['playerA'] = game.playerA
	to_json['playerB'] = game.playerB
	to_json['isTurnA'] = game.isTurnA
	to_json['needOpponent'] = game.needOpponent
	
	return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
	
	
	