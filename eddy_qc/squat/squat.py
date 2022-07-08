#!/bin/env python
"""
SQUAT (Study-wise QUality Assessment Tool)

Matteo Bastiani, FMRIB, Oxford
Martin Craig, SPMIC, Nottingham
"""
import datetime
import os
import warnings
import json

import numpy as np

import matplotlib
import matplotlib.style
from matplotlib.backends.backend_pdf import PdfPages

warnings.filterwarnings("ignore")
matplotlib.use('Agg')   # generate pdf output by default
matplotlib.interactive(False)
matplotlib.style.use('classic')

from eddy_qc.squat import (squat_report, squat_var, squat_db, squat_update)
from eddy_qc.utils import (utils, ref_page)

import argparse
import sys

__version__ = "0.0.1"

def get_subjects(fname):
    if not fname:
        raise ValueError(f"A subject list (--subjects) must be provided when using --extract")

    try:
        with open(fname) as fp:
            return [l.strip() for l in fp.readlines()]
    except IOError as exc:
        raise ValueError(f"Failed to read subject directories from {fname}: {exc}")

def main():
    """
    Generate a QC report pdf for group dMRI data.
    The script will loop through the specified qc.json files obtained using eddy_squat on 
    a set of subjects. It will produce a report pdf showing the distributions of the qc indices
    if found in the .json files. If a grouping variable is provided, extra pages will show different 
    distributions according to the grouping variable specified. If the update flag is set to true, it 
    will also update the single subject qc reports putting them into the context of the larger group. 
    Lastly, it will store the qc indices for all subjects to create a database for
    future use.

    Compulsory arguments:
       list                          Text file containing a list of squat qc folders
   
    Optional arguments:
       -g, --grouping                Text file containing grouping variable for the listed subjects
       -u, --update [group_db.json]  Update existing eddy_squat reports after generating group report or using a pre-existing [group_db.json] one
       -gdb, --group-db              Text file containing grouping variable for the database subjects
       -o, --output-dir              Output directory - default = '<eddyBase>.qc' 
    
    Output:
       output-dir/group_qc.pdf: study-wise QC report 
       output-dir/group_db.json: study-wise QC database
    """
    parser = argparse.ArgumentParser('Generalised Study-wise QUality Assessment Tool', add_help=True)
    parser.add_argument('--subjects', help='text file containing a list of single-subject QC output folders')
    parser.add_argument('--extract', action="store_true", default=False, help="Extract data from single-subject QC output into group data file")
    parser.add_argument('--group-data', help="JSON file containing previously extracted group QC data")
    parser.add_argument('--group-report', action="store_true", default=False, help="Generate group report")
    parser.add_argument('--subject-reports', action="store_true", default=False, help="Generate individual subject reports")
    parser.add_argument('-o', '--output', default="squat", help='Output directory')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not args.extract and not args.group_data:
        raise ValueError("Must specify either --extract or provide a previously extracted group data file with --group-data")
    elif args.extract and args.group_data:
        raise ValueError("Cannot specify --extract and --group-data at the same time")

    if os.path.exists(args.output):
        raise ValueError(f"Output directory {args.output} already exists - remove or specify a different name")

    os.makedirs(args.output)
    if args.extract:
        subject_list = get_subjects(args.subjects)

        sys.stdout.write('Generating group data...')
        group_data = squat_db.main(os.path.join(args.output, "group_data.json"), 'w', subject_list)
        sys.stdout.write('DONE\n')
    else:
        group_data = squat_db.main(args.group_data, 'r')

    if args.group_report:
        sys.stdout.write('Generating group QC report...')
        pdf = PdfPages(os.path.join(args.output, "group_report.pdf"))
        ref_page.main(pdf)
        squat_report.main(pdf, group_data)
        pdf.close()
        sys.stdout.write('DONE\n')
    
    if args.subject_reports:
        sys.stdout.write('Generating subject QC reports...')
        subject_list = get_subjects(args.subjects)
        for subjdir in subject_list:
            subjid = os.path.basename(subjdir)
            try:
                with open(os.path.join(subjdir, 'qc.json')) as qc_file:
                    subject_data = json.load(qc_file)
            except IOError as exc:
                raise ValueError(f"Could not read subject data for subject {subjdir}: {exc}")
            
            pdf = PdfPages(os.path.join(args.output, f"{subjid}_report.pdf"))
            ref_page.main(pdf)
            squat_report.main(pdf, group_data, subject_data)
        sys.stdout.write('DONE\n')

        # # Set the file's metadata via the PdfPages object:
        # d = pp.infodict()
        # d['Title'] = 'eddy_squat QC report'
        # d['Author'] = u'Matteo Bastiani'
        # d['Subject'] = 'group QC report'
        # d['Keywords'] = 'QC dMRI'
        # d['CreationDate'] = datetime.datetime.today()
        # d['ModDate'] = datetime.datetime.today()

if __name__ == "__main__":
    main()
