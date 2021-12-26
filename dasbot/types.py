import logging

from typing import List, Dict, Tuple
from datetime import datetime, timedelta

log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


Scores = Dict[str, Tuple[int, datetime]]
Words = List[str]
Card = Dict[str, str]
Cards = List[Card]

if __name__ == "__main__":
    pass
