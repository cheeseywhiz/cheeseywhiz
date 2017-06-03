#!/usr/bin/env python3
"""pdftxt.py input_dir output_dir pdf1 pdf2 pdf3 etc..."""

import os
import subprocess
import sys

input_dir = os.path.abspath(sys.argv[1])
output_dir = os.path.abspath(sys.argv[2])

for pdf_file in sys.argv[3:]:
    # take off the file extension and make it .txt
    file_name = pdf_file.split('.')[:-1]
    txt_file = '.'.join([*file_name, 'txt'])
    subprocess.call('pdftotext %s/%s %s/%s'
                    %(input_dir, pdf_file, output_dir, txt_file), shell=True)
