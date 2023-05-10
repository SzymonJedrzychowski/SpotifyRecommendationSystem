from modules.fuzzylogicrule import FuzzyLogicRule


class FuzzyLogic:
    """ Responsible for handling the Fuzzy Logic.

    """

    def __init__(self):
        self.rules = {}

        # Create rules.
        ruleDanceability = FuzzyLogicRule()
        ruleDanceability.addOption(0, 0, 0.3, 0.5, "low")
        ruleDanceability.addOption(0.4, 0.5, 0.55, 0.65, "medium")
        ruleDanceability.addOption(0.55, 0.7, 1, 1, "high")

        ruleEnergy = FuzzyLogicRule()
        ruleEnergy.addOption(0, 0, 0.3, 0.5, "low")
        ruleEnergy.addOption(0.2, 0.4, 0.6, 0.8, "medium")
        ruleEnergy.addOption(0.6, 0.7, 1, 1, "high")

        ruleAcousticness = FuzzyLogicRule()
        ruleAcousticness.addOption(0, 0, 0.05, 0.15, "low")
        ruleAcousticness.addOption(0.1, 0.25, 0.5, 0.7, "medium")
        ruleAcousticness.addOption(0.5, 0.7, 1, 1, "high")

        ruleInstrumentalness = FuzzyLogicRule()
        ruleInstrumentalness.addOption(0, 0, 0.05, 0.25, "low")
        ruleInstrumentalness.addOption(0, 0.25, 1, 1, "high")

        ruleTempo = FuzzyLogicRule()
        ruleTempo.addOption(0, 0, 0.25, 0.4, "low")
        ruleTempo.addOption(0.25, 0.4, 0.5, 0.6, "medium")
        ruleTempo.addOption(0.5, 0.6, 1, 1, "high")

        # Add rules.
        self.addRule(ruleDanceability, 'danceability')
        self.addRule(ruleEnergy, 'energy')
        self.addRule(ruleAcousticness, 'acousticness')
        self.addRule(ruleInstrumentalness, 'instrumentalness')
        self.addRule(ruleTempo, 'tempo')

    def addRule(self, rule: object, name: str):
        """ Add rule to the ruleset.

        :param rule: FuzzyLogicRule object.
        :param name: name of the rule.
        """

        self.rules[name] = rule

    def checkRules(self, values: dict) -> dict:
        """ Check all rules for given item (song).

        :param values: values of the song features.
        :return: dictionary with values for each Rule. 
        """

        return {
            name: rule.checkOptions(values[name])
            for (name, rule) in self.rules.items()
        }

    def checkRulesNumeric(self, values: dict) -> list:
        """ Check all rules for given item (song) returning numeric values.

        :param values: values of the song features.
        :return: array of numeric values for each Rule.
        """

        hashValues = {"low": 0, "medium": 1, "high": 2}
        results = self.checkRules(values)

        return [hashValues[i] for i in results.values()]

    def checkHash(self, values: dict) -> int:
        """ Check hash for given results of rules.

        :param values: values of the song features.
        :return: hash code of specific song style.
        """

        results = self.checkRulesNumeric(values)
        hashValue = 0

        for (index, score) in enumerate(results):
            hashValue += (3**index) * score

        return hashValue
