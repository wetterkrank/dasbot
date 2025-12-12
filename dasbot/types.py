from typing import List, Dict, Tuple
from datetime import datetime
from collections import defaultdict

from dasbot.models.dictionary import Dictionary, Level

Scores = Dict[str, Tuple[int, datetime]]
Words = List[str]
Card = Dict[str, str]
Cards = List[Card]

Dictionaries = defaultdict[Level, Dictionary]

if __name__ == "__main__":
    pass
