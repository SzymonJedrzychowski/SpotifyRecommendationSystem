from modules.fuzzylogicsrule import FuzzyLogicsRule

class FuzzyLogics:
	def __init__(self):
		self.rules = {}
		self.createRules()

	def createRules(self):
		ruleDanceability = FuzzyLogicsRule()
		ruleDanceability.addOption(0, 0, 0.3, 0.5, "low")
		ruleDanceability.addOption(0.4, 0.5, 0.55, 0.65, "medium")
		ruleDanceability.addOption(0.55, 0.7, 1, 1, "high")

		ruleEnergy = FuzzyLogicsRule()
		ruleEnergy.addOption(0, 0, 0.3, 0.5, "low")
		ruleEnergy.addOption(0.2, 0.4, 0.6, 0.8, "medium")
		ruleEnergy.addOption(0.6, 0.7, 1, 1, "high")

		ruleAcousticness = FuzzyLogicsRule()
		ruleAcousticness.addOption(0, 0, 0.05, 0.15, "low")
		ruleAcousticness.addOption(0.1, 0.25, 0.5, 0.7, "medium")
		ruleAcousticness.addOption(0.5, 0.7, 1, 1, "high")

		ruleInstrumentalness = FuzzyLogicsRule()
		ruleInstrumentalness.addOption(0, 0, 0.05, 0.25, "low")
		ruleInstrumentalness.addOption(0, 0.25, 1, 1, "high")

		ruleTempo = FuzzyLogicsRule()
		ruleTempo.addOption(0, 0, 0.25, 0.4, "low")
		ruleTempo.addOption(0.25, 0.4, 0.5, 0.6, "medium")
		ruleTempo.addOption(0.5, 0.6, 1, 1, "high")

		self.addRule(ruleDanceability, 'danceability')
		self.addRule(ruleEnergy, 'energy')
		self.addRule(ruleAcousticness, 'acousticness')
		self.addRule(ruleInstrumentalness, 'instrumentalness')
		self.addRule(ruleTempo, 'tempo')

	def addRule(self, rule, name):
		self.rules[name] = rule

	def checkRules(self, x):
		return {name: rule.checkOptions(x[name]) for (name, rule) in self.rules.items()}

	def checkRulesNumeric(self, x):
		hashValues = {
			"low": 0,
			"medium": 1,
			"high": 2
		}
		results = self.checkRules(x)

		return [hashValues[i] for i in results.values()]

	def checkHash(self, x):
		results = self.checkRulesNumeric(x)
		hash = 0

		for (index, score) in enumerate(results):
			hash += (3**index)*score

		return hash