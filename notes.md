To Do:

- Python package
  - [ ] Catalog class
    - [ ] Get (with download)
	- [ ] View (no download, metadata only)
    - [ ] Add
    - [ ] List
    - [ ] Find
    - [ ] Update (maybe)
    - [ ] Delete (maybe)
  - [ ] Dataset class
    - [ ] Use dataclass
    - [ ] Datacite metadata
    - [ ] File manifest
    - [ ] Representation: JSON
    - [ ] Representation: Markdown
  - [ ] Script to generate a mock catalog
    - [ ] To disk with JSON metadata
    - [ ] To Globus Search & Globus Collection
    - [ ] Markdown pages for Catalog and Datasets
	- [ ] Dataset pages with Schema.org embedded (seo tag?)
	- [ ] Markdown should include link to join group
	- [ ] Embed some images
datasets.
- Globus Groups
  - `/serverless/allusers/` -> Read [Serverless Data Users](https://app.globus.org/groups/260da91f-3496-11ed-b941-972795fc9504/about) All users, any may join but must accept terms.
  - `/serverless/restricted/ProjectOne/`- > Read [Serverless Data Project One](https://app.globus.org/groups/cf9d1f5b-3496-11ed-b941-972795fc9504/about) A limited group with access to a specific group of datasets. User may request access, but requests must be approved.
- Globus Collection
  - `/serverless/` [folder in demo collection](https://app.globus.org/file-manager?origin_id=6528bad5-bc02-497d-8a4f-a38547d0e72a&origin_path=%2Fserverless%2F)
  - `/serverless/public/` -> Public
  - `/serverless/allusers/` -> Read [Serverless Data Users](https://app.globus.org/groups/260da91f-3496-11ed-b941-972795fc9504/about) All users, must accept terms.
  - `/serverless/restricted/ProjectOne/`- > Read [Serverless Data Project One](https://app.globus.org/groups/cf9d1f5b-3496-11ed-b941-972795fc9504/about) A limited group with access to a specific group of 
- Mock catalog
  - [ ] Some public datasets, some in `allusers`, some in `ProjectOne`
  - [ ] Permissions in Search follow datasets
  - [ ] Markdown pages for Catalog and Datasets
  - [ ] Public pages for public and `allusers` datasets
  - [ ] ProjectOne pages not public (on Collection?), visible to all users?
- Jupyter Notebook
  - [ ] List datasets based on current level of access
  - [ ] View datasets
  - [ ] Get dataset, do something