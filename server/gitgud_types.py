from typing import Dict, Any, Tuple, Callable

Json = Dict[str, Any]
Address = Tuple[str, int]
Action = Callable[[Json], Json]
