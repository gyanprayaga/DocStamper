"""Module-wide settings."""

# The directory where your files are kept
INPUT_DIRECTORY = "/Users/gyan/Documents/DocStamperTest/Input"

# The directory for outputting stuff.
OUTPUT_DIRECTORY = "/Users/gyan/Documents/DocStamperTest/Output"

# The directory where your output bundles should go
IMAGES_DIRECTORY = f"{OUTPUT_DIRECTORY}IMAGES/"

# The directory where the load files should be created
LOADFILES_DIRECTORY = f"{OUTPUT_DIRECTORY}LOADFILES/"

# The directory where the original files should be stored
ORIGINALS_DIRECTORY = f"{OUTPUT_DIRECTORY}ORIGINALS/"

# The Bates token to prepend each file name
BATES_TOKEN = "GP"

# The max number of TIFFs to generate per PDF file
MAX_PAGES_PER_FILE = 50000

# The max number of DOCX files to convert into PDFs in one go
MAX_DOC_TO_PDF_BATCH_SIZE = 200

# Don't transform files with these names
IGNORED_FILES = []

# Original file formats to support metadata extraction and backlinking
ORIGINAL_FILE_FORMATS = [
    'DOCX',
    'DOC',
    'XLS',
    'XLSX',
    'PPT',
    'PPTX',
]

# Map each document from your input folder to its bundle
FILE_TO_BUNDLE_MAP = {
    f"{INPUT_DIRECTORY}/File to be put in the first bundle.pdf": "Bundle 1",
}
