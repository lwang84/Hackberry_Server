from django.db import models

class Vocabulary(models.Model):
	word = models.CharField(max_length=100)
	sound = models.CharField(max_length=100)
	freq = models.PositiveIntegerField()

class ActiveGames(models.Model):
	letters = models.CharField(max_length=50)
	colorStatus = models.CharField(max_length=50)
	playerA = models.PositiveIntegerField()
	playerB = models.PositiveIntegerField()
	isTurnA = models.BooleanField()
	needOpponent = models.BooleanField()
	scoreA = models.PositiveIntegerField()
	scoreB = models.PositiveIntegerField()
	lastPlayedWord = models.CharField(max_length=50)
	
class Player(models.Model):
	name = models.CharField(max_length=100)
	
class PlayedWords(models.Model):
	game = models.ForeignKey(ActiveGames)
	word = models.CharField(max_length=100)
