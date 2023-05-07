import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from pandas import DataFrame
from sklearn import preprocessing
from random import sample
import webbrowser
from threading import Thread
import json

from modules.fuzzylogics import FuzzyLogics
from modules.apiexception import APIException
from modules.fuzzylogicsrecommendation import FuzzyLogicsRecommendation
from modules.neuralnetworkrecommendation import NeuralNetworkRecommendation

class Window(QMainWindow):
	signal = pyqtSignal()
	messageSignal = pyqtSignal(str, str)
	
	def __init__(self):
		super().__init__()

		self.setWindowTitle("Spotify recommender")
		self.setMinimumSize(700, 500)
		self.suggestions = []
		self.playlistData = {"songs": [], "features": None}
		self.songsID = {}
		self.playlistAverages = {"danceability": 0, "energy": 0, "acousticness": 0, "instrumentalness": 0, "tempo": 0}
		self.spotifySuggestions = {"songs": [], "features": None}

		self.fuzzyRecommendation = FuzzyLogicsRecommendation(FuzzyLogics())
		self.networkRecommendation = NeuralNetworkRecommendation()

		try:
			with open("data/token.json") as f:
				data = json.load(f)
		except:
			self.messageSignal.emit("Error", "token.json file was not provided")

		self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=data["client_id"], client_secret=data["client_secret"]))

		self.widget = QWidget(self)

		self.initialiseWidgets()

		self.setCentralWidget(self.widget)
		self.signal.connect(self.updateTable)
		self.messageSignal.connect(self.updateMessage)

	def initialiseWidgets(self):
		font = QFont()
		font.setPointSize(18)

		smallFont = QFont()
		smallFont.setPointSize(16)

		layout = QVBoxLayout()

		playlistLayout = QHBoxLayout()
		playlistLayout.setContentsMargins(20, 20, 20, 5)

		playlistText = QLabel("Playlist ID:")
		playlistText.setFont(font)

		self.playlistID = QLineEdit()
		self.playlistID.setFont(font)

		self.playlistButton = QPushButton("Submit playlist")
		self.playlistButton.setFont(font)
		self.playlistButton.clicked.connect(self.runLoadPlaylist)

		playlistLayout.addWidget(playlistText)
		playlistLayout.addWidget(self.playlistID)
		playlistLayout.addWidget(self.playlistButton)

		buttonLayout = QHBoxLayout()
		buttonLayout.setContentsMargins(20, 5, 20, 20)

		self.suggestionButton = QPushButton("Generate song suggestions")
		self.suggestionButton.setFont(smallFont)
		self.suggestionButton.clicked.connect(self.runSuggestSongs)
		self.suggestionButton.setEnabled(False)

		buttonLayout.addWidget(self.suggestionButton)

		layout.addLayout(playlistLayout)
		layout.addLayout(buttonLayout)

		tableLayout = QHBoxLayout()

		self.tableView = QTableView()
		self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

		tableLayout.addWidget(self.tableView)
		tableLayout.setContentsMargins(20, 5, 20, 20)

		self.model = QStandardItemModel()
		self.model.setHorizontalHeaderLabels(["Song title", "Artists", "Song link"])

		for i, j in enumerate(self.suggestions):
			songTitle = QStandardItem(j[0])
			songTitle.setToolTip(j[0])
			artists = QStandardItem(j[1])
			artists.setToolTip(j[1])
			link = QStandardItem(j[2])
			self.model.setItem(i, 0, songTitle)
			self.model.setItem(i, 1, artists)
			self.model.setItem(i, 2, link)

		self.tableView.setModel(self.model)
		self.tableView.doubleClicked.connect(self.openLink)

		layout.addLayout(tableLayout)

		self.widget.setLayout(layout)

	def updateMessage(self, title, message):
		QMessageBox.about(self, title, message)

	def updateTable(self):
		for i, j in enumerate(self.suggestions):
			songTitle = QStandardItem(j[0])
			songTitle.setToolTip(j[0])
			artists = QStandardItem(j[1])
			artists.setToolTip(j[1])
			link = QStandardItem(j[2])
			self.model.setItem(i, 0, songTitle)
			self.model.setItem(i, 1, artists)
			self.model.setItem(i, 2, link)

	def runLoadPlaylist(self):
		self.playlistButton.setEnabled(False)
		self.suggestionButton.setEnabled(False)
		thread = Thread(target = self.loadPlaylist)
		thread.start()

	def loadPlaylist(self):
		playlistId = self.playlistID.text()

		try:
			dataResults = self.spotify.playlist(playlistId)
			results = self.spotify.playlist_items(playlistId)
			self.playlistData["songs"] = [i["track"]["id"] for i in results["items"]]
			while results['next']:
				results = self.spotify.next(results)
				self.playlistData["songs"].extend([i["track"]["id"] for i in results["items"]])

			if(not self.playlistData["songs"]):
				raise APIException("There is no songs in this playlist.")

			self.songsID = set(self.playlistData["songs"])

			i = 0
			self.playlistData["features"] = []

			while i*100 < len(self.playlistData["songs"]):
				features = self.spotify.audio_features(
					self.playlistData["songs"][i*100:(i+1)*100])
				self.playlistData["features"].extend(features)
				i += 1
			self.suggestionButton.setEnabled(True)
			self.messageSignal.emit("Success", f"Playlist {dataResults['name']} was loaded.")
		except APIException as E:
			self.messageSignal.emit("Error", "This playlist is empty.")
		except Exception as E:
			self.messageSignal.emit("Error", "Could not find the playlist.")

		self.playlistButton.setEnabled(True)

	def runSuggestSongs(self):
		self.playlistButton.setEnabled(False)
		self.suggestionButton.setEnabled(False)
		thread = Thread(target = self.suggestSongs)
		thread.start()

	def suggestSongs(self):
		self.suggestions = []
		self.spotifySuggestions = {"songs": [], "features": []}
		try:
			results = self.spotify.recommendations(seed_tracks=sample(self.playlistData["songs"], min(5, len(self.playlistData["songs"]))), limit=100)
			for i in results["tracks"]:
				if i["id"] not in self.songsID:
					self.spotifySuggestions["songs"].append([i["name"], [j["name"] for j in i["artists"]], i["external_urls"]["spotify"], i["id"]])

			spotifySuggestionsFeatures = self.spotify.audio_features([i[3] for i in self.spotifySuggestions["songs"]])

			self.normaliseData(spotifySuggestionsFeatures)

			# Get fuzzy recommendation
			self.fuzzyRecommendation.setDataset(self.spotifySuggestions["features"])
			fuzzySuggestion = self.fuzzyRecommendation.recommend(self.playlistData["features"])

			# Get AI recommendation
			AISuggestion = self.networkRecommendation.predict(self.playlistAverages, self.spotifySuggestions["features"], 10)
			AISuggestionSet = set(AISuggestion)
			fuzzySuggestionProcessed = []

			for i in fuzzySuggestion:
				if i not in AISuggestionSet:
					fuzzySuggestionProcessed.append(i)

			fullSuggestion = []

			numberFromFuzzy = int((len(fuzzySuggestionProcessed)+19)/20)

			fullSuggestion.extend(sample(fuzzySuggestionProcessed, numberFromFuzzy))
			fullSuggestion.extend(sample(AISuggestion, 10-numberFromFuzzy))

			for i in fullSuggestion:
				song = self.spotifySuggestions["songs"][i]
				self.suggestions.append([song[0], ", ".join([j for j in song[1]]), song[2]])
			self.signal.emit()

		except Exception as E:
			self.messageSignal.emit("Error", "Try slower.")

		self.playlistButton.setEnabled(True)
		self.suggestionButton.setEnabled(True)


	def normaliseData(self, suggestionData):
		playlistData = self.playlistData["features"]

		df = DataFrame(playlistData+suggestionData)

		df = df.drop('loudness', axis=1)
		df = df.drop('speechiness', axis=1)
		df = df.drop('liveness', axis=1)
		df = df.drop('valence', axis=1)
		df = df.drop('key', axis=1)
		df = df.drop('mode', axis=1)
		df = df.drop('time_signature', axis=1)
		df = df.drop('track_href', axis=1)
		df = df.drop('analysis_url', axis=1)
		df = df.drop('duration_ms', axis=1)
		df = df.drop('type', axis=1)
		df = df.drop('id', axis=1)
		df = df.drop('uri', axis=1)

		scaler = preprocessing.MinMaxScaler()
		df[['tempo']] = scaler.fit_transform(df[['tempo']])

		df1 = df.iloc[:len(playlistData), :]
		df2 = df.iloc[len(playlistData):, :]

		self.playlistAverages = df1.mean().to_dict()

		self.playlistData["features"] = df1.to_dict('records')
		self.spotifySuggestions["features"] = df2.to_dict('records')

	def openLink(self, clickedRow):
		try:
			webbrowser.open(self.suggestions[clickedRow.row()][2])
		except:
			pass