from docoracle.blocks.type_block import TypeBlock


class SimpleClass:
    """
    This is my simple class!

    :param int A:
    :param float B:
    """

    def __init__(self, A: int, B: float):
        self.A = A
        self.B = B

    def multiply(self) -> float:
        """
        Multiply internal numbers together
        """
        return self.A * self.B


def my_function(a: int) -> float:
    """
    This is my function!

    :param a: A number of some kind: or something
    """
    return 2.0 * a
