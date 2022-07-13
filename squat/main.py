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

import matplotlib
import matplotlib.style

warnings.filterwarnings("ignore")
matplotlib.use('Agg')   # generate pdf output by default
matplotlib.interactive(False)
matplotlib.style.use('classic')

from .report import Report
from .data import GroupData, SubjectData, read_json

import argparse
import sys

from ._version import __version__

def get_subjects(subjdir, fname):
    if fname:       
        try:
            with open(fname) as fp:
                return [l.strip() for l in fp.readlines()]
        except IOError as exc:
            raise ValueError(f"Failed to read subject IDs from {fname}: {exc}")
    else:
        try:
            return sorted(os.listdir(subjdir))
        except IOError as exc:
            raise ValueError(f"Failed to find any subject directories in {subjdir}: {exc}")

def main():
    """
    Tool for generating QC reports for single subjects and groups
    """
    parser = argparse.ArgumentParser('Generalised Study-wise QUality Assessment Tool', add_help=True)
    parser.add_argument('--subjdir', default=".", help='Path to directory containing single-subject output')
    parser.add_argument('--subjects', help='Path to text file containing a list of subject IDs. If not specified will use all subdirectories of --subjdir')
    parser.add_argument('--qcpath', default="qc.json", help='Path to QC output file relative to subject directory')
    parser.add_argument('--extract', action="store_true", default=False, help="Extract data from single-subject QC output into group data file")
    parser.add_argument('--group-data', help="JSON file containing previously extracted group QC data")
    parser.add_argument('--group-report', action="store_true", default=False, help="Generate group report")
    parser.add_argument('--subject-reports', action="store_true", default=False, help="Generate individual subject reports")
    parser.add_argument('--report-def', help="JSON report definition file")
    parser.add_argument('-o', '--output', default="squat", help='Output directory')
    parser.add_argument('--overwrite', action="store_true", default=False, help='If specified, overwrite any existing output')
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if not args.extract and not args.group_data:
        raise ValueError("Must specify either --extract or provide a previously extracted group data file with --group-data")
    elif args.extract and args.group_data:
        raise ValueError("Cannot specify --extract and --group-data at the same time")

    if args.group_report or args.subject_reports:
        if not args.report_def:
            raise ValueError("Report definition not given (--report-def)")
        report_def = read_json(args.report_def, "report definition")

    if os.path.exists(args.output) and not args.overwrite:
        raise ValueError(f"Output directory {args.output} already exists - remove or specify a different name")
    os.makedirs(args.output, exist_ok=True)

    if args.extract or args.subject_reports:
        subjids = get_subjects(args.subjdir, args.subjects)
        subjqcdata = []
        for subjid in subjids:
            subjdir = os.path.join(args.subjdir, subjid)
            subjqcdata.append(SubjectData(subjid, os.path.join(subjdir, args.qcpath)))

    if args.extract:
        sys.stdout.write('Generating group data...')
        sys.stdout.flush()
        group_data = GroupData(subject_datas=subjqcdata)
        group_data.write(os.path.join(args.output, "group_data.json"))
        sys.stdout.write('DONE\n')
    else:
        group_data = GroupData(fname=args.group_data)

    if args.group_report:
        sys.stdout.write('Generating group QC report...')
        sys.stdout.flush()
        report = Report(report_def, group_data)
        report.save(os.path.join(args.output, "group_report.pdf"))
        sys.stdout.write('DONE\n')
    
    if args.subject_reports:
        sys.stdout.write('Generating subject QC reports...')
        sys.stdout.flush()
        for subject_data in subjqcdata:
            sys.stdout.write(subject_data.subjid + " ")
            sys.stdout.flush()
            report = Report(report_def, group_data, subject_data)
            report.save(os.path.join(args.output, f"{subject_data.subjid}_report.pdf"))
        sys.stdout.write('DONE\n')

if __name__ == "__main__":
    main()
