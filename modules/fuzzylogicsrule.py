class FuzzyLogicsRule:
	def __init__(self):
		self.options = {}

	def addOption(self, x1, x2, x3, x4, name):
		self.options[name] = (x1, x2, x3, x4)

	def checkOption(self, x, name):
		p = self.options[name]

		if x < p[0]:
			return 0

		if x < p[1]:
			return (1/(p[1]-p[0]))*(x-p[0])

		if x <= p[2]:
			return 1

		if x < p[3]:
			return 1-(1/(p[3]-p[2]))*(x-p[2])

		if p[2] == 1 and x > 1:
			return 1

		return 0

	def checkOptions(self, x):
		results = {i: self.checkOption(x, i) for i in self.options}
		return max(results, key=results.get)