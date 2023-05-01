"""Main thread."""

import os
from datetime import datetime
from typing import List
import shutil

import pypdfium2 as pdfium
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont

from settings import (
    INPUT_DIRECTORY,
    IMAGES_DIRECTORY,
    FILE_TO_BUNDLE_MAP,
    MAX_PAGES_PER_FILE,
    ORIGINAL_FILE_FORMATS,
    LOADFILES_DIRECTORY,
    ORIGINALS_DIRECTORY,
    BATES_TOKEN,
)
from logger import logger
from symbols import FileMetadata, PDFDocument
from utils import extractFileMetadata
from loadfile import OPTLoadFile, OPTRecord, DATLoadFile, DATRecord

bates_num = 1

file_metadata: List[FileMetadata] = []


def indexFiles(directory) -> List[FileMetadata]:
    """Go through all the files in specified directory and index them."""

    """
    
    xyz.pdf
    xyz_2.pdf
    ABC/
        1.pdf
    
    """

    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)

        if os.path.isfile(f):
            file = extractFileMetadata(f)

            # Link with original file.
            if file['extension'] == 'PDF':

                for file_format in ORIGINAL_FILE_FORMATS:
                    original_file_path = os.path.splitext(
                        file['path'])[0] + f".{file_format.lower()}"

                    if os.path.exists(original_file_path):
                        original_file = extractFileMetadata(original_file_path)

                        file['original_file'] = original_file
                        file['date_created'] = original_file['date_created']
                        file['date_modified'] = original_file['date_modified']

                        logger.info(
                            f"Linked original file metadata to {file['name']}")

            file_metadata.append(file)

            logger.info(f"Indexed {file['name']}")

        elif os.path.isdir(f):
            # recursively index...
            indexFiles(f)


def incrementBatesNumber() -> str:
    """Generate the bates number."""
    global bates_num

    delim = "_"

    # format bates number
    if (bates_num < 10):
        bates_num_str = f"0000{bates_num}"
    elif (bates_num < 100):
        bates_num_str = f"000{bates_num}"
    elif (bates_num < 1000):
        bates_num_str = f"00{bates_num}"
    elif (bates_num < 10000):
        bates_num_str = f"0{bates_num}"
    else:
        bates_num_str = str(bates_num)

    bates_num += 1

    return f"{BATES_TOKEN}{delim}{bates_num_str}"


def getOriginalFilePaths(file: FileMetadata, bundle_label: str, bates_id: str):
    original_file = file
    if file['original_file']:
        original_file = file['original_file']

    source_path = original_file['path']
    destination_path = f"{ORIGINALS_DIRECTORY}{bundle_label}/{bates_id}.{original_file['extension'].lower()}"

    return source_path, destination_path


def stampImage(
    image_file_path: str,
    file: FileMetadata,
    opt: OPTLoadFile,
    page_index: int,
    page_count: int,
    bundle_label: str,
    bates_id: str,
):
    """Stamp the image with a Bates number and record in load files."""
    fontfile = font_manager.findfont('DM Mono')
    myFont = ImageFont.truetype(fontfile, 20)
    img = Image.open(image_file_path)
    I1 = ImageDraw.Draw(img)
    I1.text((20, 20), bates_id, font=myFont, fill=(0, 0, 0))

    logger.info(f"Stamped {bates_id}")

    img.save(image_file_path)

    # If its the first page, save the original file
    if page_index == 0:
        source_path, destination_path = getOriginalFilePaths(
            file=file, bundle_label=bundle_label, bates_id=bates_id)
        shutil.copy2(source_path, destination_path)

    # Add OPT record
    document_break = True if page_index == 0 else False
    opt_record = OPTRecord(
        bates_number=bates_id,
        volume_label=bundle_label,
        image_file_path=image_file_path,
        document_break=document_break,
        page_count=page_count if document_break else None,
    )

    opt.addRecord(opt_record)


def convertJPGToTIFF(file: FileMetadata, opt: OPTLoadFile, dat: DATLoadFile, bundle_label: str):
    """Given a JPG, convert to TIFF image."""

    # Create an image file with the bates number.
    im = Image.open(file['path'])
    rgb_im = im.convert('RGB')
    bates_id = incrementBatesNumber()

    image_name = f"{bates_id}.tiff"
    image_file_path = f"{IMAGES_DIRECTORY}{bundle_label}/{image_name}"
    rgb_im.save(image_file_path)

    stampImage(
        image_file_path=image_file_path,
        file=file,
        opt=opt,
        page_index=0,
        page_count=1,
        bundle_label=bundle_label,
        bates_id=bates_id,
    )

    # Add DAT record
    _, destination_path = getOriginalFilePaths(
        file=file, bundle_label=bundle_label, bates_id=bates_id)
    dat_record = DATRecord(
        BEGBATES=bates_id,
        ENDBATES=bates_id,
        DOCTITLE=file['name_without_ext'],
        MODDATE=file['date_modified'].strftime("%Y%m%d"),
        PAGES=1,
        FILE_EXT=file['extension'],
        ORIGINAL_FILE_PATH=destination_path,
    )
    dat.addRecord(dat_record)


def convertPDFToImage(file: FileMetadata, opt: OPTLoadFile, dat: DATLoadFile, bundle_label: str):
    """Given a PDF, convert all its pages to TIFF image."""

    # Load a document
    pdf = pdfium.PdfDocument(file['path'])

    page_count = len(pdf)

    # Save all the pages
    BEGBATES, ENDBATES = "", ""

    for i in range(min([page_count, MAX_PAGES_PER_FILE])):
        try:
            page = pdf.get_page(i)
        except IndexError:
            break

        # render a single page (in this case: the first one)
        page = pdf.get_page(i)

        pil_image = page.render_to(
            pdfium.BitmapConv.pil_image,
            scale=100 / 50,
        )

        # Create an image file with the bates number.
        bates_id = incrementBatesNumber()
        image_name = f"{bates_id}.tiff"
        image_file_path = f"{IMAGES_DIRECTORY}{bundle_label}/{image_name}"
        pil_image.save(image_file_path)

        if i == 0:
            # first page
            BEGBATES = bates_id

        if i == page_count - 1:
            # last page
            ENDBATES = bates_id

        stampImage(
            image_file_path=image_file_path,
            file=file,
            opt=opt,
            page_index=i,
            page_count=page_count,
            bundle_label=bundle_label,
            bates_id=bates_id,
        )

    # Add DAT record
    _, destination_path = getOriginalFilePaths(
        file=file, bundle_label=bundle_label, bates_id=BEGBATES)
    dat_record = DATRecord(
        BEGBATES=BEGBATES,
        ENDBATES=ENDBATES,
        DOCTITLE=file['name_without_ext'],
        MODDATE=file['date_modified'].strftime("%Y%m%d"),
        PAGES=page_count,
        FILE_EXT=file['extension'],
        ORIGINAL_FILE_PATH=destination_path,
    )
    dat.addRecord(dat_record)


def run():
    """Main thread."""

    # Create folder organization.
    for d in [IMAGES_DIRECTORY, LOADFILES_DIRECTORY, ORIGINALS_DIRECTORY]:
        os.makedirs(d)

    # 1. Index the files and save the file metadata.
    indexFiles(INPUT_DIRECTORY)

    bundles = {}

    # Map the files to bundles.
    for file in file_metadata:

        try:
            bundle = FILE_TO_BUNDLE_MAP[file['path']]

            if bundle not in bundles:
                bundles[bundle] = []
            bundles[bundle].append(file)

        except KeyError:
            logger.warning(f"No mapping exists for '{file['path']}'.")

    # There are also mappings which pull all the files in a given folder.
    for path, bundle_label in FILE_TO_BUNDLE_MAP.items():
        if path.endswith("*"):

            lookup_path = path[:-1]

            # TODO: this is a lazy list comp, maybe we can speed this up?
            files_to_bundle = [x for x in file_metadata if (
                os.path.dirname(x['path']) + "/") == lookup_path]

            if bundle_label not in bundles:
                bundles[bundle_label] = []

            logger.info(
                f"Wildcard mapping added {len(files_to_bundle)} files to bundle.")

            bundles[bundle_label].extend(files_to_bundle)

    completed_bundles = []

    for bundle_label, files in bundles.items():

        print(f"\nCreating {bundle_label} bundle with {len(files)} documents:")

        # For each group, reorder the list by last_modified.
        files.sort(key=lambda f: f['date_modified'])

        # Create directories where bundles will be created.
        os.makedirs(IMAGES_DIRECTORY + bundle_label)
        os.makedirs(ORIGINALS_DIRECTORY + bundle_label)

        # Create load files
        opt = OPTLoadFile(
            bundle_label=bundle_label
        )
        dat = DATLoadFile(
            bundle_label=bundle_label
        )

        bundle_count = 0
        bundled_docs = []

        for file in files:

            if file['extension'] == 'PDF':
                convertPDFToImage(file, opt, dat, bundle_label)
                logger.info(f"Added '{file['name']}' to bundle.")
                bundle_count += 1
                bundled_docs.append(file['name'])

            elif file['extension'] == 'JPG':
                convertJPGToTIFF(file, opt, dat, bundle_label)
                logger.info(f"Added '{file['name']}' to bundle.")
                bundle_count += 1
                bundled_docs.append(file['name'])

            else:
                logger.error(
                    f"Unable to process file '{file['name']}' because type {file['extension']} is not PDF or JPG.")
                continue

        try:
            opt.export()
            dat.export()

            completed_bundles.append({
                "label": bundle_label,
                "count": bundle_count,
                "docs": bundled_docs,
            })

        except Exception as e:
            logger.error(
                f"Unable to generate load files for bundle {bundle_label}. Error: {e}")

    logger.info("Finished running. Generated bundles:")

    for b_ in completed_bundles:
        logger.info(f"Bundle {b_['label']} has {b_['count']} documents:")

        for doc in b_["docs"]:
            logger.info(f"* {doc}")


if __name__ == "__main__":

    run()
