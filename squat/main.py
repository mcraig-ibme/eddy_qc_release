#!/bin/env python
"""
SQUAT: Study-wise QUality Assessment Tool

Command line interface

Matteo Bastiani, FMRIB, Oxford
Martin Craig, SPMIC, Nottingham
"""
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

from . import report, data, refs

import argparse
import sys

from ._version import __version__

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
    Tool for generating QC reports for single subjects and groups
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
        group_data = data.main(os.path.join(args.output, "group_data.json"), 'w', subject_list)
        sys.stdout.write('DONE\n')
    else:
        group_data = data.main(args.group_data, 'r')

    if args.group_report:
        sys.stdout.write('Generating group QC report...')
        pdf = PdfPages(os.path.join(args.output, "group_report.pdf"))
        refs.main(pdf)
        report.main(pdf, group_data)
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
            refs.main(pdf)
            report.main(pdf, group_data, subject_data)
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
