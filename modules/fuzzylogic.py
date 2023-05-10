from modules.fuzzylogicfeature import FuzzyLogicFeature


class FuzzyLogic:
    """ Responsible for handling the Fuzzy Logic.

    """

    def __init__(self):
        self.features = {}

        # Create features.
        featureDanceability = FuzzyLogicFeature()
        featureDanceability.addFunction(0, 0, 0.3, 0.5, "low")
        featureDanceability.addFunction(0.4, 0.5, 0.55, 0.65, "medium")
        featureDanceability.addFunction(0.55, 0.7, 1, 1, "high")

        featureEnergy = FuzzyLogicFeature()
        featureEnergy.addFunction(0, 0, 0.3, 0.5, "low")
        featureEnergy.addFunction(0.2, 0.4, 0.6, 0.8, "medium")
        featureEnergy.addFunction(0.6, 0.7, 1, 1, "high")

        featureAcousticness = FuzzyLogicFeature()
        featureAcousticness.addFunction(0, 0, 0.05, 0.15, "low")
        featureAcousticness.addFunction(0.1, 0.25, 0.5, 0.7, "medium")
        featureAcousticness.addFunction(0.5, 0.7, 1, 1, "high")

        featureInstrumentalness = FuzzyLogicFeature()
        featureInstrumentalness.addFunction(0, 0, 0.05, 0.25, "low")
        featureInstrumentalness.addFunction(0, 0.25, 1, 1, "high")

        featureTempo = FuzzyLogicFeature()
        featureTempo.addFunction(0, 0, 0.25, 0.4, "low")
        featureTempo.addFunction(0.25, 0.4, 0.5, 0.6, "medium")
        featureTempo.addFunction(0.5, 0.6, 1, 1, "high")

        # Add membership functions for each feature.
        self.addFeature(featureDanceability, 'danceability')
        self.addFeature(featureEnergy, 'energy')
        self.addFeature(featureAcousticness, 'acousticness')
        self.addFeature(featureInstrumentalness, 'instrumentalness')
        self.addFeature(featureTempo, 'tempo')

    def addFeature(self, feature: object, name: str):
        """ Add feature to the Fuzzy Logic system.

        :param feature: fuzzyLogicFeature object.
        :param name: name of the feature.
        """

        self.features[name] = feature

    def checkFeatures(self, values: dict) -> dict:
        """ Check all features for given item (song).

        :param values: values of the song features.
        :return: dictionary with values for each feature. 
        """

        return {
            name: feature.checkFunctions(values[name])
            for (name, feature) in self.features.items()
        }

    def checkFeaturesNumeric(self, values: dict) -> list:
        """ Check all features for given item (song) returning numeric values.

        :param values: values of the song features.
        :return: array of numeric values for each feature.
        """

        hashValues = {"low": 0, "medium": 1, "high": 2}
        results = self.checkFeatures(values)

        return [hashValues[i] for i in results.values()]

    def checkHash(self, values: dict) -> int:
        """ Check hash for given results of features.

        :param values: values of the song features.
        :return: hash code of specific song style.
        """

        results = self.checkFeaturesNumeric(values)
        hashValue = 0

        for (index, score) in enumerate(results):
            hashValue += (3**index) * score

        return hashValue
