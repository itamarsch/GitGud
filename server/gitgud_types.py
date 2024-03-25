from typing import Dict, Any, Tuple, Callable, Literal

Json = Dict[str, Any]
Address = Tuple[str, int]
Action = Callable[[Json], Json]

IssuePr = Literal["Issue", "PR"]


commit_page_size = 20
