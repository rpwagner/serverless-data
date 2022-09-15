from dataclasses import dataclass, asdict
from typing import List, Set
from pytablewriter import MarkdownTableWriter
from serverless_data.dc import Citable
from serverless_data.dataset import Dataset

@dataclass
class Catalog(Citable):
    # DataCite resourceTypeGeneral = Collection
    resourceTypeGeneral: str = 'Collection'
    # to do: this should be a datetime object
    tags: List[str] = None
    datasets: List[Dataset] | None = None
    # UUID of the Globus Search index
    _index = str = ''
    # UUID of the Globus collection
    _collection = str = ''
    _basepath = str = ''

    def _as_markdown(self, h_prefix = ''):
        md = super()._as_markdown(h_prefix)
        if self.datasets:
            table_name = 'Datasets'
            dset_headers = ['Name', 'ID', 'Creator', 'Created', 'Number of Files']
            dset_rows = []
            for dset in self.datasets:
                dset_rows.append([dset.name, dset.identifier, dset.creator,
                                  dset.created, len(dset.manifest)])
            writer = MarkdownTableWriter(
                        table_name=table_name,
                        headers=dset_headers,
                        value_matrix=dset_rows,
                        )
            md += writer.dumps()
        return md

    def as_json(self):
        d  = asdict(self)
        del d['datasets']
        return json.dumps(d)
