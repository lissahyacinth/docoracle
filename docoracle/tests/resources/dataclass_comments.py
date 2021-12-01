from dataclasses import dataclass


@dataclass
class DataClassWithComments:
    # LHS Integer
    A: int
    # RHS Float
    B: float

    def multiply(self) -> float:
        """
        Multiply internal numbers together
        """
        return self.A * self.B
