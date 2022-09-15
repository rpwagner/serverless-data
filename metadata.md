# Metadata Standards

- [DataCite Metadata Schema 4.4](https://support.datacite.org/docs/datacite-metadata-schema-44) [Citation](https://doi.org/10.14454/3w3z-sa82)
- Schema.org
- [Describing a Dataset](https://github.com/ESIPFed/science-on-schema.org/blob/master/guides/Dataset.md)


[Example dataset](https://schema.datacite.org/meta/kernel-4.4/example/datacite-example-dataset-v4.xml)

## Crosswalk

[How can I map different metadata formats to the DataCite schema?](https://support.datacite.org/docs/how-can-i-map-different-metadata-formats-to-the-datacite-xml)

Citation metadata, required

| DataCite XML| schema.org |
| identifier| @id | 
| title | name |
| creator | author |
| publisher | publisher | 
| publicationYear | datePublished |
| version | version
| resourceTypeGeneral | @type | 

Discovery metadata

| DataCite XML | schema.org |
| description | description|
| subject | keywords |
| rights | license |
| relatedIdentifier | isPartOf|
