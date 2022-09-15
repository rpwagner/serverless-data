from dataclasses import dataclass
import hashlib
import os
from typing import List, Set

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
class Dataset:
    internal_id: str
    # to do: this should be a datetime object
    created: str = ''
    # short name of the lab member (Kyle, Angelica, Phil, etc.)
    authors: str | List[str] | Set[str] | None = None
    description = ''
    tags: str | Set[str] = None
    manifest: DataFile | List[DataFile] | Set[DataFile] | None = None
    # Globus search subject ID
    subject: str = ""
