class APIException(Exception):
    """ Custom exception for the API errors.

    """

    def __init__(self, message: str):
        super().__init__(self, message)
