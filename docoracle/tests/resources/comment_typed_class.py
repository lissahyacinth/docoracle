class CommentTypedClass:
    """
    This is my comment typed class!

    :param int A:
    :param float B:
    """

    def __init__(self, A, B):
        self.A = A
        self.B = B

    def multiply(self) -> float:
        """
        Multiply internal numbers together
        """
        return self.A * self.B
