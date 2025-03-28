class InvalidThresholdError(Exception):
    """Exception raised if an invalid threshold is  computed.
       """

    def __init__(self, message="The given threshold is not valid for preprocessing - must be > 2."):
        self.message = message
        super().__init__(self.message)
