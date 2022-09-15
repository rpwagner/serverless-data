from dataclasses import dataclass
from typing import List, Set
from serverless_data.dc import Citable
from serverless_data.dataset import Dataset

@dataclass
class Catalog(Citable):
    # DataCite resourceTypeGeneral = Collection
    resourceTypeGeneral: str = 'Collection'
    # to do: this should be a datetime object
    tags: str | Set[str] = None
    datasets: List[Dataset] | Set[Dataset] | None = None
    # UUID of the Globus Search index
    _index = str = ''
    # UUID of the Globus collection
    _collection = str = ''
    _basepath = str = ''

