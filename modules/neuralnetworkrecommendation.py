from tensorflow import keras
import numpy as np


class NeuralNetworkRecommendation:
    """ Recommends the songs based on the Neural Network system.

    """

    def __init__(self):
        # Load the model.
        self.model = keras.models.load_model('data/model')

    def predict(self, averages: dict, std: dict, suggestions: list, count: int) -> tuple:
        """ Predict fitting values for songs.

        :param averages: averages of features of the playlist.
        :param std: standard deviation of features of the playlist.
        :param suggestions: list with songs to predict from.
        :param count: number of best songs to select.
        :return: list of recommended songs AND list of predicted values with indexes 
        """

        # Preprocess data.
        data = np.array(self.preprocessData(averages, std, suggestions))

        # Predict and reshape the data.
        values = self.model.predict(data, verbose=0)
        values = values.reshape((len(suggestions),))

        # Sort the results.
        resultsTogether = [[j, i] for i, j in enumerate(values)]
        resultsTogether = sorted(resultsTogether, reverse=True)

        # Get recommendations.
        recommendations = [i[1] for i in resultsTogether[0:count]]

        return recommendations, resultsTogether

    def preprocessData(self, averages: dict, std: dict, suggestions: list) -> list:
        """ Preprocess the data before predict method.

        :param averages: averages of features of the playlist.
        :param std: standard deviation of features of the playlist.
        :param suggestions: list with songs to predict from.
        :return: array of processed data.
        """

        processedData = []

        for row in suggestions:
            # Combine the features of the song, averages and std.
            temp = [row["danceability"], row["energy"], row["acousticness"],
                    row["instrumentalness"], row["tempo"]] + list(averages.values()) + list(std.values())
            processedData.append(temp)

        return processedData
