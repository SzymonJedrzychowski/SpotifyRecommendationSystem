from random import sample

class FuzzyLogicsRecommendation:
	def __init__(self, agent):
		self.agent = agent
		self.suggestionData = {i: [] for i in range(243)}

	def setDataset(self, dataset):
		for (index, row) in enumerate(dataset):
			r = self.agent.checkHash(row)
			self.suggestionData[r].append(index)

	def recommend(self, playlistData):
		playlistSample = sample(playlistData, min(20, len(playlistData)))

		toGet = {}
		for row in playlistSample:
			sampleHash = self.agent.checkHash(row)
			if sampleHash not in toGet:
				toGet[sampleHash] = 0
			toGet[sampleHash] += 5

		data = []
		for (hash, number) in toGet.items():
			data += sample(self.suggestionData[hash], min(number, len(self.suggestionData[hash])))

		return data