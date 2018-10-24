#!/usr/bin/env python3

"""
@author:    George Ekman
@email:     george.ekman@madisoncountryday.org
@license:   MIT
@date:      2018-10-23
@version:   1.0.0

This is a command line tool to bulk generate the Student IDs.

Outline:
========

1. Load modules
2. Configurate the commandline interface
3. Process the commandline arguments into variables
4. Initiate debug mode, if enabled
5. Check the validity of the arguments/paths
6. Open the templates
7. Open the data file and process it
    1. Get the student information
    2. Fill the information into the template
    3. Render the SVG templates into PDFs
    4. Merge the front and back PDFs into one
"""

#### Load modules

import argparse                     # Commandline argument processor
import barcode                      # To generate the barcodes
import base64                       # To embed the images in the SVG
import cairosvg                     # To conver the svg to a pdf
import csv                          # Parse the data file (which is a CSV file)
import os                           # Create and manage/manipulate paths
from PyPDF2 import PdfFileMerger    # Merge the front and back of the IDs

#### Configurate the commandline interface

# Initiate the parser with a description of this tool
parser = argparse.ArgumentParser(description='Bulk generates student IDs from \
    a template, csv data file, and images')
# Add the `--template` argument as required
parser.add_argument('--template', required=True, help='The path to the        \
    template SVG directory')
# Add the `--data` argument as required
parser.add_argument('--data', required=True, help='The path to the CSV data   \
    file')
# Add the `--images` argument as required
parser.add_argument('--images', required=True, help='The path to the          \
    directory of student photo images')
# Add the `--out` argument as optional
parser.add_argument('--out', default='./id_gen_out', help='The path to the    \
    desired output directory. Defaults to \'./id_gen_out\'. Note: will fail   \
    if the directory (or the tmp subdirectory) does not already exist.')
# Add the `--debug` argument as optional; (if included: True; otherwise: False)
parser.add_argument('--debug', action='store_true', help='Enable debug output')

#### Process the commandline arguments into variables

# Parse the arguments into `args`
args = parser.parse_args()
# The path to the template SVG to load
template_path = args.template
# The path to the data file to load and parse
data_path = args.data
# The path to the images directory to find the needed photos
images_path = args.images
# The path to the output PDFs
output_path = args.out
# Whether to output debug information to stdout
debug = args.debug

#### Initiate debug mode, if enabled

if debug:
    # Let the user know debug mode is enabled
    print("Debug mode enabled")
    # Output argument values as stored
    print(f"template_path: {template_path}")
    print(f"data_path: {data_path}")
    print(f"images_path: {images_path}")
    print(f"debug: {str(debug)}") # debug is a bool, not a str

#### Check the validity of the arguments/paths

# If the `template_path`s does not exist, exit with an error
if (not os.path.exists(os.path.join(template_path, 'front.svg'))
    or not os.path.exists(os.path.join(template_path, 'back.svg'))):
    exit(f"Error: {os.path.join(template_path, 'front.svg')} or "             \
        f"{os.path.join(template_path, 'back.svg')} does not exist")

# If the `data_path` does not exist, exit with an error
if not os.path.exists(data_path):
    exit(f"Error: {data_path} does not exist")

# If the `images_path` does not exist, exit with an error
if not os.path.exists(images_path):
    exit(f"Error: {images_path} does not exist")

# If the `output_path` directory or `output_path`/tmp does *not* exist
if not os.path.exists(os.path.join(output_path, 'tmp')):
    if debug: print(f"{output_path} or {os.path.join(output_path, 'tmp')}"    \
        "does not exist. Creating it...")
    # Create the tmp subdirectory and any other necessary parent directories
    os.makedirs(os.path.join(output_path, 'tmp'))

#### Open the templates

# Read the contents of the front template at `template_path` into
# `template_front`
with open(template_path + "front.svg") as f:
    template_front = f.read()

# Read the contents of the back template at `template_path` into
# `template_back`
with open(template_path + "back.svg") as f:
    template_back = f.read()

if debug:
    print("`template_front` contents:")
    print(template_front)
    print("`template_back` contents:")
    print(template_back)

#### Open the data file and process it

with open(data_path) as datafile:
    data = csv.reader(datafile)
    for row in data:
        #### Get the student information

        # row[0]: first
        # row[1]: last
        # row[2]: year
        # row[3]: id
        # row[4]: photo

        # In debug mode, output the row separated with commas
        if debug: print(', '.join(row))

        # If the row is a header row, continue to the next row
        if row == ['First', 'Last', 'Year', 'ID Number', 'Photo Number']:
            continue
        # If the photo cell is empty, continue to the next row.
        # This would happen if the student isn't real (e.g. Fake Student) or
        # they weren't there on picture day.
        if row[4] == '':
            print(f"Student {row[0]} {row[1]} does not have a photo. "        \
            "Skipping...")
            continue

        # Read the contents of the image at `images_path`/<year>/<photo>.jpg
        # and convert it into a base64 string
        with open(os.path.join(images_path, row[2], row[4] + '.jpg'), 'rb')   \
            as f:
            # NOTE: If the student is off scale for the box, make sure the svg
            # element for the element is using the width and height of the
            # box/outline, and not the width and height of the image and a
            # scale!

            # The [2:-1] 'removes' the first two characters (b') and the last
            # character (') of the string
            image_str = str(base64.b64encode(f.read()))[2:-1]

        # Create the barcode object:
        #     `barcode.get_barcode_class('code128')(row[3])`
        # Render (to an svg string) the barcode object with a `module_width` of
        # 1 and disabled text:
        #     .render(writer_options={'module_width': 1, 'write_text': False})
        # Remove the b' from the beginning and the ' from the end:
        #     [2:-1]
        # Encode the rendered string in base64:
        #     base64.b64encode(...)
        # Convert the encoded base64 to a str:
        #     str(...)
        # Remove the (new) b' from the beginning and the ' from the end:
        #     [2:-1]
        id_barcode = str(base64.b64encode(
                cairosvg.svg2png(
                    bytestring=barcode.get_barcode_class('code128')(row[3])
                        .render(
                            writer_options={
                                'module_width': 1,
                                'write_text': False
                            }
                        ),
                    scale=10
                )
            ))[2:-1]

        if debug:
            print("Barcode of id " + row[3] + ":")
            print(id_barcode)

        #### Fill the information into the template

        # Replace all of the template strings in the front:
        # <!-- NAME -->     becomes     row[0] + ' ' + row[1]
        # <!-- YEAR -->     becomes     row[2]
        # <!-- ID -->       becomes     row[3]
        # <!-- PHOTO -->    becoems     image_str
        id_front = template_front                                             \
            .replace('<!-- NAME -->', row[0] + ' ' + row[1])                  \
            .replace('<!-- YEAR -->', row[2]).replace('<!-- ID -->', row[3])  \
            .replace('<!-- PHOTO -->', image_str)

        # Replace all of the template strings in the back:
        # <!-- BARCODE -->     becomes     id_barcode
        id_back = template_back                                               \
            .replace('<!-- BARCODE -->', id_barcode)

        if debug:
            print("ID Front:")
            print(id_front)
            print("ID Back:")
            print(id_back)

        #### Render the SVG templates into PDFs

        # Pass the svg string as a bytestring encoded in UTF-8 to CairoSVG and
        # write the output pdf to
        # output_path + '/' + row[3] + '-<front or back>.pdf'
        #
        # The width/height numbers involved some trial and error but these are
        # the size needed to output the correct PDF size for the IDs.
        cairosvg.svg2pdf(
            bytestring=id_front.encode('utf-8'),
            write_to=os.path.join(output_path, 'tmp', row[3] + '-front.pdf'),
            parent_width=323,
            parent_height=204
        )
        cairosvg.svg2pdf(
            bytestring=id_back.encode('utf-8'),
            write_to=os.path.join(output_path, 'tmp', row[3] + '-back.pdf'),
            parent_width=323,
            parent_height=204
        )

        #### Merge the front and back PDFs into one

        # Initialize the PDF merger
        merger = PdfFileMerger()
        # The path to the front of the id
        front = os.path.join(output_path, 'tmp', row[3] + '-front.pdf')
        # The path to the back of the id
        back = os.path.join(output_path, 'tmp', row[3] + '-back.pdf')
        # Add the front to the output PDF
        merger.append(front)
        # Add the back to the output PDF
        merger.append(back)
        # Open/create the output PDF file in write byte mode
        with open(os.path.join(output_path, row[3] + '.pdf'), 'wb') as output:
            # Write the output to the output PDF
            merger.write(output)

# Just to be nice, let's say we are done, with a newline just to be clear.
print("\nDone.")
