"""Convert DOCX to PDF"""

import os
from typing import List

import docx2pdf

from symbols import FileMetadata
from utils import extractFileMetadata
from settings import INPUT_DIRECTORY, MAX_DOC_TO_PDF_BATCH_SIZE, IGNORED_FILES


file_metadata: List[FileMetadata] = []

def indexFiles(directory) -> List[FileMetadata]:
    """Go through all the files in specified directory and index them."""

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
    
        if os.path.isfile(f):
            file_metadata.append(extractFileMetadata(f))

        elif os.path.isdir(f):
            # recursively index...
            indexFiles(f)


def run():
    """Convert all DOCX files to PDFs."""
    
    # 1. Index the files
    indexFiles(
        directory=INPUT_DIRECTORY
    )

    # 2. Get the DOCX files
    files_to_convert = []
    files_excluded = []

    for file in file_metadata:
        if file.extension == 'DOCX':
            pdf_version = os.path.splitext(file.path)[0] + ".pdf"

            if os.path.exists(pdf_version) or (file.name in IGNORED_FILES):
                files_excluded.append(file)
            else:
                files_to_convert.append(file)

        else:
            files_excluded.append(file)

    print("Converting these DOC files: ", [x.name for x in files_to_convert])
    print("Not converting these files: ", [x.name for x in files_excluded])

    files_converted = []

    # 3. Convert the DOCX files to PDFs
    for file in files_to_convert[:MAX_DOC_TO_PDF_BATCH_SIZE]:

        output_file_path = os.path.splitext(file.path)[0] + ".pdf"

        docx2pdf.convert(file.path, output_file_path)

        files_converted.append(file)

    print("Successfully converted these files: ", [x.name for x in files_converted])

    files_left_to_convert = len(files_to_convert) - len(files_converted)
    print(f"{files_left_to_convert} files left to convert.")


if __name__ == "__main__":
    run()