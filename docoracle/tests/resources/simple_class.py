class SimpleClass:
    """
    This is my simple class!

    :param A int
    :param B float
    """

    def __init__(self, A: int, B: float):
        self.A = A
        self.B = B

    def multiply(self) -> float:
        """
        Multiply internal numbers together
        """
        return self.A * self.B
