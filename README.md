# DocStamper

DocStamper is a simple, open-source tool for sorting, Bates stamping, and packaging documents.

These Python scripts were original created to serve a client who needed to prepare documents for a subpoena. Below is a brief description of what each script does.

`script.py`
This script takes files in PDF format and maps them into "production folders". Then, these PDFs are chronologically ordered, spliced into TIFF images, and Bates stamped. Finally, a load file in DAT and OPT formats is created to help the recipient load the documents into their document management software.

`convert_to_pdf.py`
This script converts any DOCX files in a given directory to PDF. It checks which files already have PDF counterparts and skips them, so you don't have to worry about overriding any files.

## Example use case

Say you receive a subpoena asking you to send some documents for a contract you worked on with a client. 

Let's say you have a filesystem of structure:

```
accounts/
   client_1.docx
   client_2.docx
notes/
    notes_03_15_2022.docx
    notes_04_15_2022.docx
```

The requesting agency wants the files to be organized into bundles like this:

```
BUNDLE_A/
   client_1.docx
   notes_03_15_2022.docx
BUNDLE_B/
   client_2.docx
   notes_04_15_2022.docx
```

such that they receive them in this format:

```
BUNDLE_A/
   JOE_0001.tiff
   JOE_0002.tiff
   JOE_0003.tiff
   JOE_0004.tiff
BUNDLE_B/
   JOE_0005.tiff
   JOE_0006.tiff
   JOE_0007.tiff
   JOE_0008.tiff
```
where `JOE` is the moniker the agency assigns to your production of documents.

Here's how you do that:

## Usage

### Configuration
Make sure to modify the `settings.py` with the corresponding values. Here are the settings you'll want to change:

- `INPUT_DIRECTORY`: Set this to directory where your files are kept
- `OUTPUT_DIRECTORY`: Set this to the directory where the bundles should be output
- `FILE_TO_BUNDLE_MAP`: Configure how you want each file to mapped from your file system into the bundle


### Running

1. Make sure to modify the `settings.py` as needed.
2. Run `convert_to_pdf.py` to convert any DOCX files to PDFs.
3. Run `script.py`.
4. Enjoy your bundled, Bates stamped TIFF files!

---

Note: This repositiory is not being actively maintained.
