EIGHTBITS: int = ...
PARITY_ODD: int = ...
STOPBITS_ONE: int = ...


class Serial:
    def __init__(self,
                 path: str,
                 *,
                 bytesize: int,
                 parity: int,
                 stopbits: int,
                 timeout: int = ...,
                 rtscts: bool = ...) -> None:
        ...

    def write(self, data: bytes | list[int]) -> int:
        ...

    def read(self, length: int) -> bytes:
        ...
