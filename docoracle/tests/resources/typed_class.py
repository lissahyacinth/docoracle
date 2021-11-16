class TypedClass:
    """
    This is my typed class!
    """

    def __init__(self, A: int, B: float):
        self.A = A
        self.B = B

    def multiply(self) -> float:
        """
        Multiply internal numbers together
        """
        return self.A * self.B
