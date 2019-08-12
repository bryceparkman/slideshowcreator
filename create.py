import io
import sys
import os
import json
import requests
import lyricsgenius
import time
import pygame
from google_images_download import google_images_download
from textblob import TextBlob

#Set fail token
FAIL = "~"

#Setup genius lyrics
client_access = "your-token-here"
genius = lyricsgenius.Genius(client_access)
genius.remove_section_headers = True
genius.verbose = False

#Audio/Transcript
audioFile = ""
transcriptFile = ""

#Global variables
audioJson = ""
fileName = ""
parsedWords = []
allWords = []

def getSongLyrics():
	global transcriptFile
	'''
	For getting the lyrics transcript from a song, requires user to have the mp3 of the song.
	Saves transcript to file named [song title trimmed and lowercase].txt
	Allows gentle to attempt to align the lyrics to timings within the song to ease music video creation.
	Uses lyrics genius module, which requires user to have an access token.
	'''
	if(not os.path.exists("{0}\\transcript.txt".format(fileName))):
		print("Enter that artist's name")
		artist = input()
		print("Enter that song's name.")
		song = input()
		song = genius.search_song(song, artist)
		print("Got lyrics for {} by {} and created text file in directory".format(song.title,song.artist))
		with open("{0}\\transcript.txt".format(fileName),"w+") as f:
			f.write(song.lyrics)
	transcriptFile = "{0}\\transcript.txt".format(fileName)


def alignAudio():
	global audioJson
	'''
	Curl command attained from via information on the lowerquality gentle github
	Parsed via trillworks curl command->python requests parser. (https://curl.trillworks.com/)
	Downloads the JSON file of the alignment once complete
	'''
	if(not os.path.exists("{0}\\align.json".format(fileName))):
		params = (
	    	('async', 'false'),
		)

		files = {
	    	'audio': (audioFile, open(audioFile, 'rb')),
	    	'transcript': (transcriptFile, open(transcriptFile, 'rb')),
		}	

		print("Aligning audio...")
		response = requests.post('http://192.168.99.100:8765/transcriptions', params=params, files=files)
		audioJson = response.json()
		with open("{0}\\align.json".format(fileName),"w+") as f:
			json.dump(audioJson,f)
		print("Done!")
	else:
		audioJson = json.load(open("{0}\\align.json".format(fileName)))

def createWordTimeGroups():
	'''
	Takes the json and parses the important words into an array with a start and end timing (data provided by gentle)
	<unk> refers to a word that was timed but the phonemes couldn't be parsed correctly (something we don't care
	about for this project, just the words themselves.) If the word can't be parsed it just passes in a fail token to the arrays.
	'''
	global parsedWords
	global allWords
	parsedWords = []
	allWords = []
	words = audioJson["words"]
	for word in words:
		important = False
		#If word was found
		if word["case"] == "success":
			w = ""
			if word["alignedWord"] == "<unk>":
				#Pass in transcript word if phonemes couldn't be parsed
				w = word["word"]
			else:
				w = word["alignedWord"] #Pass in the correctly identified word from the transcript

			#Get part of speech of word
			pos = TextBlob(word["alignedWord"]).tags[0][1]

			#Checks if word is "important" and not a preposition or otherwise before adding
			if  pos != "IN" and pos != "CC" and pos != "DT" and pos != "TO" and w != "is": 
				#Add word to be googled to list
				parsedWords.append(w)
				#Set important tag
				important = True

			#Append an array which represents the word and its start and end timings given by gentle.
			#Also indicates if it is in parsed words, so o(n) operation isn't needed later
			allWords.append([w,word["start"],word["end"],important])
		#Otherwise pass in fail token
		else:
			parsedWords.append(FAIL)
			allWords.append([FAIL])


def downloadImages():
	'''
	Uses the google_images_download library to download an image form google relating to the
	word that was aligned from the audio.
	'''
	response = google_images_download.googleimagesdownload()
	print("Downloading images...")
	#Stops the output to the console, otherwise it takes up the whole screen
	text_trap = io.StringIO()
	sys.stdout = text_trap

	for i in range(0,len(parsedWords)):
		if(parsedWords[i] != FAIL and not os.path.isdir("downloads\\%s" % parsedWords[i])):
			arguments = {
				"keywords":  parsedWords[i],
				"format": "jpg",
				"limit": 1,
				"size": "medium"
			}
			#Download images
			response.download(arguments)
	#Resumes console output
	sys.stdout = sys.__stdout__
	print("Done!")
			

def play():
	'''
	Uses pygame to load the images, then plays the audio with synced up images.
	'''
	pygame.init()

	gameDisplay = pygame.display.set_mode((1200,600))

	white = (255,255,255)

	images = []

	for word in parsedWords:
		if(word != FAIL):
			#Set directory for image
			p = "downloads\\%s" % word
			#Downloads the first file in the folder containing the image for this word
			first_file = next(os.path.join(p, f) for f in os.listdir(p) if os.path.isfile(os.path.join(p, f)))
			#Load the image into an array
			images.append(pygame.image.load(first_file))

	#Play audio
	pygame.mixer.init()
	pygame.mixer.music.load(audioFile)
	pygame.mixer.music.play(0)
	#Start a "timer"
	tStart = time.time()

	#For looping through downloaded images
	count = 0

	for i in range(len(allWords)):
		#If the current word has a picture associated with it
		if allWords[i][0] != FAIL and allWords[i][3]:
			#Find how long the audio clip has been running
			deltaT = time.time() - tStart
			#Find how long to wait
			delay = allWords[i][1]-deltaT
			#If the image is to be displayed now/in the future
			if(delay >= 0):
				time.sleep(delay)
				gameDisplay.blit(images[count],(0,0))
				pygame.display.update()
			#If the images have to catch up with the audio it doesnt draw an image, then goes to the next one
			count+=1

if len(sys.argv) == 2:
	audioFile = "{0}\\audio.mp3".format(sys.argv[1])
	transcriptFile = "{0}\\transcript.txt".format(sys.argv[1])
	fileName = sys.argv[1]
if len(sys.argv) == 3 and sys.argv[1] == "-s":
	audioFile = "{0}\\audio.mp3".format(sys.argv[2])
	fileName = sys.argv[2]
	getSongLyrics()

alignAudio()
createWordTimeGroups()
downloadImages()
play()
pygame.quit()