from dataclasses import dataclass, asdict
from typing import List, Set

@dataclass
class Citable:
    # attributes described in DataCite XML, schema.org order
    # | title | name |
    name: str
    # | identifier| @id |
    identifier: str = ''
    # | creator | author |
    creator: str | List[str] | Set[str] | None = None
    # | publisher | publisher | 
    publisher: str | List[str] | Set[str] | None = None
    # | publicationYear | datePublished |
    created: str = ''
    # | version | version
    version: str = ''
    # | description | description|
    description: str = ''
    # | subject | keywords |
    keywords: str | List[str] | Set[str] | None = None
    # | rights | license |
    license: str = ''
    # For DataCite, this is RelatedIdentifier, relationType = isPartOf
    # Used for datasets to reference collection
    # | relatedIdentifier | isPartOf |
    isPartOf: str | List[str] | Set[str] | None = None
    # Defined by subclass
    # | resourceTypeGeneral | @type | 
    resourceTypeGeneral: str = ''

    citation_fields = ['name', 'identifier', 'creator',
                'publisher', 'created', 'version', 'description',
                'keywords', 'license', 'isPartOf',
                'resourceTypeGeneral']
    
    def _as_schema_org(self):
        name_map = {'resourceTypeGeneral': '@type',
                    'identifier': '@id',
                    'creator': 'author',
                    'created': 'datePublished'}
        d = asdict(self)
        d['@context'] = 'https://schema.org/'
        for k in list(d):
            if not k in self.citation_fields:
                del d[k]
        for old, new in name_map.items():
            d[new] = d[old]
            del d[old]
        return d
