from typing import Literal, NewType, TypeAlias

BookID = NewType("BookID", int)

StatusType: TypeAlias = Literal["pending", "confirmed", "failed"]
