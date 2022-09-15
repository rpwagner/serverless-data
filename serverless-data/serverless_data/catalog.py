from dataclasses import dataclass
from typing import List, Set
from serverless_data.dataset import Dataset

@dataclass
class Catalog:
    name: str
    internal_id: str = ''
    # to do: this should be a datetime object
    created: str = ''
    # short name of the lab member (Kyle, Angelica, Phil, etc.)
    authors: str | List[str] | Set[str] | None = None
    description = ''
    tags: str | Set[str] = None
    datasets: List[Dataset] | Set[Dataset] | None = None
    _index = str = ''
    _collection = str = ''
    _basepath = str = ''

