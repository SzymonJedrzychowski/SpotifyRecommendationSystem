from random import sample


class FuzzyLogicRecommendation:
    """ Recommends the songs based on the Fuzzy Logic system.

    """

    def __init__(self, agent: object):
        self.agent = agent
        self.suggestionData = {i: [] for i in range(243)}

    def setDataset(self, dataset: list):
        """ Calculates the hash codes for songs in the dataset.

        :param dataset: list of songs to choose the recommendations from.
        """

        for (index, row) in enumerate(dataset):
            r = self.agent.checkHash(row)
            self.suggestionData[r].append(index)

    def recommend(self, playlistData: list) -> list:
        """ Recommend songs.

        :param playlistData: data of the playlist for the recommendation.
        :return: indexes of recommended songs.
        """

        # Get sample of songs from the playlist.
        playlistSample = sample(playlistData, min(20, len(playlistData)))

        # Save how many songs with given hash code should be added.
        toGet = {}
        for row in playlistSample:
            sampleHash = self.agent.checkHash(row)
            if sampleHash not in toGet:
                toGet[sampleHash] = 0
            toGet[sampleHash] += 5

        # Get sample songs with given hash codes.
        data = []
        for (hash, number) in toGet.items():
            data += sample(self.suggestionData[hash],
                           min(number, len(self.suggestionData[hash])))

        return data
