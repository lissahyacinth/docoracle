from dataclasses import dataclass


@dataclass
class DataClassNoComments:
    A: int
    B: float

    def multiply(self) -> float:
        """
        Multiply internal numbers together
        """
        return self.A * self.B
