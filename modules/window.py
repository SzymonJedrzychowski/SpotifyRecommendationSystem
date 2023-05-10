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
from copy import deepcopy

from modules.fuzzy import FuzzyLogic
from modules.apiexception import APIException
from modules.fuzzylogicrecommendation import FuzzyLogicRecommendation
from modules.neuralnetworkrecommendation import NeuralNetworkRecommendation


class Window(QMainWindow):
    """ Creates the windows with user interface.

    """

    # Variables used to display specific messages.
    signal = pyqtSignal()
    messageSignal = pyqtSignal(str, str)

    def __init__(self):
        super().__init__()
        self.ifWorks = False

        self.setWindowTitle("Spotify recommender")
        self.setMinimumSize(700, 500)

        try:
            self.setWindowIcon(QIcon("resources/music.png"))
        except:
            pass

        self.suggestions = []
        self.playlistData = {"songs": [], "features": []}
        self.songsID = {}
        self.spotifySuggestions = {"songs": [], "features": []}

        self.playlistAverages = {}
        self.playlistStd = {}

        self.fuzzyRecommendation = FuzzyLogicRecommendation(FuzzyLogic())

        self.signal.connect(self.updateTable)
        self.messageSignal.connect(self.updateMessage)

        try:
            self.networkRecommendation = NeuralNetworkRecommendation()
        except:
            self.messageSignal.emit("Error", "Model was not provided.")
            return

        # Load the credentails to the API.
        try:
            with open("data/token.json") as f:
                data = json.load(f)
        except:
            self.messageSignal.emit(
                "Error", "token.json file was not provided.")
            return

        # Connect to the API.
        try:
            self.spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(
                client_id=data["client_id"], client_secret=data["client_secret"]))
        except:
            self.messageSignal.emit(
                "Error", "Could not connect to the API.")
            return

        self.widget = QWidget(self)
        self.initialiseWidgets()
        self.setCentralWidget(self.widget)

        self.ifWorks = True

    def initialiseWidgets(self):
        """ Set up the user interface.

        """

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
        self.model.setHorizontalHeaderLabels(
            ["Song title", "Artists", "Song link"])

        # Create model for song table.
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

    def updateMessage(self, title: str, message: str):
        """ Display a message window. 

        :param title: title of the window.
        :param message: message text.
        """

        messageBox = QMessageBox()
        messageBox.setWindowTitle(title)
        messageBox.setText(message)

        # Select proper icon.
        try:
            if (title == "Success"):
                messageBox.setWindowIcon(QIcon("resources/check.png"))
            else:
                messageBox.setWindowIcon(QIcon("resources/error.png"))
        except:
            pass

        # Display the message box.
        messageBox.exec_()

    def updateTable(self):
        """ Update the table with the data of recommended songs.

        """

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
        """ Run separate thread for loading playlist.

        """

        # Disable the buttons.
        self.playlistButton.setEnabled(False)
        self.suggestionButton.setEnabled(False)

        thread = Thread(target=self.loadPlaylist)
        thread.start()

    def loadPlaylist(self):
        """ Loads the data of the playlist using the API.

        """

        # Get the text from the text input box.
        playlistId = self.playlistID.text()

        try:
            # Get the songs from the playlist.
            dataResults = self.spotify.playlist(playlistId)
            results = self.spotify.playlist_items(playlistId)
            self.playlistData["songs"] = [i["track"]["id"]
                                          for i in results["items"]]
            while results['next']:
                results = self.spotify.next(results)
                self.playlistData["songs"].extend(
                    [i["track"]["id"] for i in results["items"]])

            # Raise error if the playlist is empty.
            if (not self.playlistData["songs"]):
                raise APIException("There is no songs in this playlist.")

            self.songsID = set(self.playlistData["songs"])

            # Load the features of the songs using the API.
            i = 0
            self.playlistData["features"] = []
            while i*100 < len(self.playlistData["songs"]):
                features = self.spotify.audio_features(
                    self.playlistData["songs"][i*100:(i+1)*100])
                self.playlistData["features"].extend(features)
                i += 1

            # Remove songs that did not have features.
            for i in range(self.playlistData["features"].count(None)):
                self.playlistData["features"].remove(None)

            # Enable the button for song recommendation.
            self.suggestionButton.setEnabled(True)

            # Emit the message to show the message window.
            self.messageSignal.emit(
                "Success", f"Playlist {dataResults['name']} was loaded.")

        except APIException as E:
            self.messageSignal.emit("Error", "This playlist is empty.")
        except Exception as E:
            self.messageSignal.emit("Error", "Could not find the playlist.")

        # Enable the button.
        self.playlistButton.setEnabled(True)

    def runSuggestSongs(self):
        """ Run separate thread for recommending songs.

        """

        # Disable the buttons.
        self.playlistButton.setEnabled(False)
        self.suggestionButton.setEnabled(False)

        thread = Thread(target=self.suggestSongs)
        thread.start()

    def suggestSongs(self):
        """  Suggests the song by combining Neural Network and Fuzzy Logic recommendation systems.

        """

        self.suggestions = []
        self.spotifySuggestions = {"songs": [], "features": []}
        try:
            # Get the suggestions from the API and remove songs that are already in the playlist.
            results = self.spotify.recommendations(seed_tracks=sample(
                self.playlistData["songs"], min(5, len(self.playlistData["songs"]))), limit=100)
            for i in results["tracks"]:
                if i["id"] not in self.songsID:
                    self.spotifySuggestions["songs"].append(
                        [i["name"], [j["name"] for j in i["artists"]], i["external_urls"]["spotify"], i["id"]])

            # Get the features of the songs.
            spotifySuggestionsFeatures = self.spotify.audio_features(
                [i[3] for i in self.spotifySuggestions["songs"]])

            # Prepare the data.
            self.prepareData(spotifySuggestionsFeatures)

            # Get fuzzy recommendation
            self.fuzzyRecommendation.setDataset(
                self.spotifySuggestions["features"])
            fuzzySuggestion = self.fuzzyRecommendation.recommend(
                self.playlistData["features"])
            fuzzySuggestionSet = set(fuzzySuggestion)

            # Get AI recommendation
            AISuggestion, resultsTogether = self.networkRecommendation.predict(
                self.playlistAverages, self.playlistStd, self.spotifySuggestions["features"], 10)
            AISuggestionSet = set(AISuggestion)
            fuzzySuggestionProcessed = []

            # Approve the songs that had the highest result from Neural Network and were suggested by the Fuzzy Logic.
            for i in resultsTogether:
                if i[1] in fuzzySuggestionSet:
                    fuzzySuggestionProcessed.append(i[1])

                # Get max of 5 recommendations.
                if len(fuzzySuggestionProcessed) == 5:
                    break

            fullSuggestion = []

            # Get the number of recommended songs and add them to the full list.
            numberFromFuzzy = len(fuzzySuggestionProcessed)
            fullSuggestion.extend(fuzzySuggestionProcessed)

            # Approve the songs that had the highest result from Neural Network and were not suggested by the Fuzzy Logic (so that there is 10 songs in total).
            AISuggestionCopy = [i for i in deepcopy(
                AISuggestion[0:10]) if i not in fullSuggestion]
            fullSuggestion.extend(AISuggestionCopy[:10-numberFromFuzzy])

            # Append the data of the songs.
            for i in fullSuggestion:
                song = self.spotifySuggestions["songs"][i]
                self.suggestions.append(
                    [song[0], ", ".join([j for j in song[1]]), song[2]])

            # Emit the signal to load the data into the table.
            self.signal.emit()

        except Exception as E:
            self.messageSignal.emit("Error", "Try slower.")

        # Enable the button.
        self.playlistButton.setEnabled(True)
        self.suggestionButton.setEnabled(True)

    def prepareData(self, suggestionData: list):
        """ Prepare and normalise the data

        """

        playlistData = self.playlistData["features"]

        # Use DataFrame to combine the data.
        df = DataFrame(playlistData+suggestionData)

        # Remove unused values.
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

        # Use MinMaxScaler for tempo normalisation.
        scaler = preprocessing.MinMaxScaler()
        df[['tempo']] = scaler.fit_transform(df[['tempo']])

        # Divide the data back to original sizes.
        df1 = df.iloc[:len(playlistData), :]
        df2 = df.iloc[len(playlistData):, :]

        # Calculate the average and standard deviation.
        self.playlistAverages = df1.mean().to_dict()
        self.playlistStd = df1.std().to_dict()

        # Update the variables.
        self.playlistData["features"] = df1.to_dict('records')
        self.spotifySuggestions["features"] = df2.to_dict('records')

    def openLink(self, clickedRow: object):
        """ Open the song in the browser by double clicking 

        """

        try:
            webbrowser.open(self.suggestions[clickedRow.row()][2])
        except:
            pass
