class FuzzyLogicFeature:
    """ Creates singular Fuzzy Logic for one feature.

    """

    def __init__(self):
        self.functions = {}

    def addFunction(self, x1: float, x2: float, x3: float, x4: float, name: str):
        """ Adding function (trapezoidal membership function) to given feature.

        :param x1: x from where function starts to grow (y = 0).
        :param x2: x where function stops growing (y = 1).
        :param x3: x from where function starts to decrease (y = 1).
        :param x4: x where function stops decreasing (y = 0).
        """

        self.functions[name] = (x1, x2, x3, x4)

    def checkFunction(self, x: float, name: str) -> float:
        """ Check value for selected membership function. 

        :param x: value of x to check.
        :param name: name of membership function to check.
        :return: value for given membership function.
        """

        p = self.functions[name]

        if x < p[0]:
            return 0.0

        if x < p[1]:
            return (1/(p[1]-p[0]))*(x-p[0])

        if x <= p[2]:
            return 1.0

        if x < p[3]:
            return 1-(1/(p[3]-p[2]))*(x-p[2])

        if p[2] == 1 and x > 1:
            return 1.0

        return 0.0

    def checkFunctions(self, x: float) -> str:
        """ Check values for all membership functions. 

        :param x: value of x to check.
        :return: name of the chosen membership function.
        """

        results = {i: self.checkFunction(x, i) for i in self.functions}
        return max(results, key=results.get)
