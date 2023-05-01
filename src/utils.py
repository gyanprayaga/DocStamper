"""Utils shared across package."""

from datetime import datetime
import os

from symbols import FileMetadata 


def extractFileMetadata(filepath) -> FileMetadata:
    """Given a filename, get its metadata and content and store it."""

    # TODO: If this is a PDF with a corresponding non-PDF, use the non-PDF's last
    # modified (assume it was exported).

    filename = os.path.basename(filepath)
    extension = os.path.splitext(filename)[1][1:].upper() # This should be a PDF
    filename_without_ext = os.path.splitext(filename)[0]

    date_modified = datetime.fromtimestamp(os.path.getmtime(filepath))
    date_created = datetime.fromtimestamp(os.path.getctime(filepath))

    dirpath = os.path.dirname(filepath)
    dirname = os.path.basename(dirpath)

    return FileMetadata(
        name=filename,
        name_without_ext=filename_without_ext,
        path=filepath,
        extension=extension,
        date_modified=date_modified,
        date_created=date_created,
        original_file=None,
    )