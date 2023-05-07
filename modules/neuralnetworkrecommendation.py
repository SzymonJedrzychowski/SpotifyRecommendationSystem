from tensorflow import keras
import numpy as np

class NeuralNetworkRecommendation:
	def __init__(self):
		self.model = keras.models.load_model('data/model')

	def predict(self, averages, suggestions, count):
		data = np.array(self.preprocessData(averages, suggestions))
		values = self.model.predict(data, verbose=0)
		values = values.reshape((len(suggestions),))
		recommendations = list(np.argpartition(values, -count)[-count:])
		return recommendations

	def preprocessData(self, averages, suggestions):
		processedData = []
		for row in suggestions:
			temp = [row["danceability"], row["energy"], row["acousticness"], row["instrumentalness"], row["tempo"]] + list(averages.values())
			processedData.append(temp)
		return processedData