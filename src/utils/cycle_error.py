class NegativeCycleError(Exception):
    """Exception raised upon discovering a negatice cycle.
    """
    def __init__(self,cycle = None, message="A negative cycle was found!"):
        self.message = message
        self.cycle = cycle
        super().__init__(self.message)

    def get_cycle(self):
        return self.cycle if self.cycle is not None else None