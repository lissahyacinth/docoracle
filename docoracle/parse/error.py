from typing import Generic, TypeVar, List

T = TypeVar("T")


class ParseError(BaseException):
    pass


class ParseStatus(Generic[T]):
    inner: T
    errors: List[ParseError]
