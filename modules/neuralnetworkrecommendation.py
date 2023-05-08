from tensorflow import keras
import numpy as np

class NeuralNetworkRecommendation:
	def __init__(self):
		self.model = keras.models.load_model('data/model')

	def predict(self, averages, std, suggestions, count):
		data = np.array(self.preprocessData(averages, std, suggestions))
		values = self.model.predict(data, verbose=0)
		values = values.reshape((len(suggestions),))

		resultsTogether = [[j, i] for i, j in enumerate(values)]
		resultsTogether = sorted(resultsTogether, reverse=True)

		recommendations = [i[1] for i in resultsTogether[0:count]]
		return recommendations, resultsTogether

	def preprocessData(self, averages, std, suggestions):
		processedData = []
		for row in suggestions:
			temp = [row["danceability"], row["energy"], row["acousticness"], row["instrumentalness"], row["tempo"]] + list(averages.values()) + list(std.values())
			processedData.append(temp)
		return processedData