from dataclasses import dataclass, asdict
import urllib.parse
import hashlib
import os
from typing import List, Set
import json
from pytablewriter import MarkdownTableWriter
from serverless_data.dc import Citable

base_app_path = 'https://app.globus.org/file-manager?origin_id=6528bad5-bc02-497d-8a4f-a38547d0e72a&origin_path='

# probably should store all constants in one location
BUF_SIZE = 4194304  # read in 4MB chunks

@dataclass
class DataFile:
    filename: str
    length: int = 0
    sha512: str = ''
    url: str = ''
    # local_filename should not be serialized to go into the catalog
    local_filename: str = ''

    def __post_init__(self):
        # check to see if this is a local file
        if not self.local_filename:
            if os.path.exists(self.filename):
                self.local_filename = self.filename
                self.filename = os.path.basename(self.local_filename)
                self.update()

    def update(self, overwrite: bool = False):
        if not self.length or overwrite:
            self._update_length()
        if not self.sha512 or overwrite:
            self._update_hash()

    def _update_length(self):
        self.length = os.path.getsize(self.local_filename)

    def _update_hash(self):
        h = hashlib.new('sha512')
        with open(self.local_filename, 'rb') as f:
            while True:
                data = f.read(BUF_SIZE)
                if not data:
                    break
                h.update(data)
        self.sha512 = h.hexdigest()


@dataclass
class Dataset(Citable):
    # DataCite resourceTypeGeneral = Dataset
    resourceTypeGeneral: str = 'Dataset'
    tags: str | Set[str] = None
    manifest: List[DataFile] | None = None
    # Globus search subject ID
    subject: str = ""
    license: str = ''
    access_policy: str = 'public'
    groupname: str = ''
    groupuuid: str = ''

    def _as_markdown(self, h_prefix = ''):
        md = super()._as_markdown(h_prefix)
        md += '{}## Data Access\n'.format(h_prefix)
        if self.access_policy == 'public':
            md += 'This dataset is publicy available.\n'
        elif self.access_policy == 'allusers':
            md += 'Access to this dataset requires accepting terms and conditions. '
            md += 'Join the Globus Group [{}]({}) to acknowledge acceptance.\n\n'.format(self.groupname,self.groupuuid)
            md += '[Request Access](https://app.globus.org/groups/{}/join")\n\n'.format(self.groupuuid)
        else:
            md += 'Access to this dataset requires approval. '
            md += 'Request to to join the Globus Group [{}]({}) for access.\n\n'.format(self.groupname, self.groupuuid)
            md += '[Request Access](https://app.globus.org/groups/{}/join)\n\n'.format(self.groupuuid)
        md += 'This dataset is available via Globus Transfer or HTTPS.\n'

        path = '/serverless/{}/'.format(self.identifier)
        path = urllib.parse.quote(path)
        md += '[Click here]({}{}) to view the files in the Globus web app.\n'.format(base_app_path, path)

        images = []
        if self.manifest:
            table_name = 'Files'
            f_headers = ['File Name', 'Size (Bytes)', 'Hash']
            f_rows = []
            for f in self.manifest:
                name = f.filename
                if f.url:
                    name = '[{}]({})'.format(name, f.url)
                    if f.filename[-3:] == 'png':
                        images.append('![{}]({})'.format(f.filename, f.url))
                short_hash = '{}...'.format(f.sha512[:8])
                f_rows.append([name, f.length, short_hash])
            writer = MarkdownTableWriter(
                        table_name=table_name,
                        headers=f_headers,
                        value_matrix=f_rows,
                        )
            md += writer.dumps()
        if images:
            md += '{}## Images\n'.format(h_prefix)
            for image in images:
                md += '{} '.format(image)
        md += '\n\n'
        md += '[Back to catalog](../)\n\n'

        return md

    def as_json(self):
        return json.dumps(asdict(self))
    
