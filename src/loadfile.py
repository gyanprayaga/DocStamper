"""Loadfiles"""
from typing import TypedDict, List, Optional, Union
import os

from settings import LOADFILES_DIRECTORY, OUTPUT_DIRECTORY

from logger import logger

class OPTRecord(TypedDict):
    """Type for OPT record."""
    bates_number: str
    volume_label: str
    image_file_path: str
    document_break: bool
    page_count: Optional[int]


class DATRecord(TypedDict):
    """Type for DAT record."""
    BEGBATES: str
    ENDBATES: str
    DOCTITLE: str
    MODDATE: str
    PAGES: int
    FILE_EXT: str
    ORIGINAL_FILE_PATH: str


class LoadFile():

    def __init__(self, bundle_label: str):
        """Constructs the load file."""
        self._bundle_label: str = bundle_label
        self._records: List[Union[OPTRecord, DATRecord]] = []

    def addRecord(self, record: Union[OPTRecord, DATRecord]):
        """Add a record to the load file."""
        self._records.append(record)


class OPTLoadFile(LoadFile):
    """Opticon load file class."""

    def export(self):
        """Export the load file as OPT format."""
        self._records: List[OPTRecord]

        opt_path = LOADFILES_DIRECTORY + f"{self._bundle_label}.opt"

        fp = open(opt_path, 'w')

        for i, r in enumerate(self._records):

            line = f"{r['bates_number']},{r['volume_label']},{_getRelativeWindowsPath(r['image_file_path'])},{'Y' if r['document_break'] else ''},{r['page_count'] or ''}"
            
            if i < len(self._records) - 1:
                line += "\n"
            
            fp.write(line)

        logger.info(f"Wrote OPT load file to {opt_path}")

        fp.close()


class DATLoadFile(LoadFile):
    """Concordance DAT load file class."""

    def export(self):
        """Export the load file as DAT format."""
        Q = 'þ'
        D = '\x14'
        C = '®'

        self._records: List[DATRecord]

        dat_path = LOADFILES_DIRECTORY + f"{self._bundle_label}.dat"

        fp = open(dat_path, 'w')

        # header
        fp.write(f"{Q}BEGBATES{Q}{D}ENDBATES{Q}{D}{Q}DOCTITLE{Q}{D}{Q}MODDATE{Q}{D}{Q}PAGES{Q}{D}{Q}FILE_EXT{Q}{D}{Q}ORIGINAL_FILE_PATH{Q}{C}\n")

        for i, r in enumerate(self._records):

            relative_file_path = _getRelativeWindowsPath(r['ORIGINAL_FILE_PATH'])

            line = f"{Q}{r['BEGBATES']}{Q}{D}{Q}{r['ENDBATES']}{Q}{D}{Q}{r['DOCTITLE']}{Q}{D}{Q}{r['MODDATE']}{Q}{D}{Q}{r['PAGES']}{Q}{D}{Q}{r['FILE_EXT']}{Q}{D}{Q}{relative_file_path}{Q}"
            
            if i < len(self._records):
                line += f"{C}\n"
            
            fp.write(line)

        logger.info(f"Wrote DAT load file to {dat_path}")

        fp.close()


def _getRelativeWindowsPath(file_path: str) -> str:
    """Get the relative path and format Windows-style."""

    relative_path = os.path.relpath(file_path, OUTPUT_DIRECTORY)
    return relative_path.replace('/', '\\')