#!/bin/env python
"""
SQUAT: Study-wise QUality Assessment Tool

Command line interface

Matteo Bastiani, FMRIB, Oxford
Martin Craig, SPMIC, Nottingham
"""
import os
import warnings
import logging
import argparse
import sys

import matplotlib
import matplotlib.style

warnings.filterwarnings("ignore")
matplotlib.use('Agg')   # generate pdf output by default
matplotlib.interactive(False)
matplotlib.style.use('classic')

from ._version import __version__
from .report import Report
from .data import GroupData, SubjectData, read_json
from .test.data import generate_test_data

LOG = logging.getLogger(__name__)

def _get_subjects(subjdir, fname):
    if fname:       
        try:
            with open(fname) as fp:
                return [l.strip() for l in fp.readlines() if l.strip()]
        except IOError as exc:
            raise ValueError(f"Failed to read subject IDs from {fname}: {exc}")
    else:
        try:
            return sorted(os.listdir(subjdir))
        except IOError as exc:
            raise ValueError(f"Failed to find any subject directories in {subjdir}: {exc}")

def _setup_logging(args):
    if args.debug:
        logging.getLogger("squat").setLevel(logging.DEBUG)
    else:
        logging.getLogger("squat").setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stderr)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)

def main():
    """
    Tool for generating QC reports for single subjects and groups
    """
    parser = argparse.ArgumentParser('Generalised Study-wise QUality Assessment Tool', add_help=True)
    parser.add_argument('--subjdir', default=".", help='Path to directory containing single-subject output')
    parser.add_argument('--subjects', help='Path to text file containing a list of subject IDs. If not specified will use all subdirectories of --subjdir')
    parser.add_argument('--qcpaths', default=["qc.json"], nargs="+", help='Paths to all JSON QC output files relative to subject directory')
    parser.add_argument('--extract', action="store_true", default=False, help="Extract data from single-subject QC output into group data file")
    parser.add_argument('--group-data', help="JSON file containing previously extracted group QC data")
    parser.add_argument('--group-report', action="store_true", default=False, help="Generate group report")
    parser.add_argument('--subject-reports', action="store_true", default=False, help="Generate individual subject reports")
    parser.add_argument('--subject-report-path', help="Path within subject dir to save individual subject reports. If not specified, subject reports are all stored in the output directory")
    parser.add_argument('--report-def', help="JSON report definition file")
    parser.add_argument('--comparison-dists', help="JSON file containing mapping from variable name to distribution mean/std from some external group")
    parser.add_argument('--amber-sigma', type=float, default=1, help="Number of standard deviations away from the mean for a value to be flagged as an 'amber' outlier")
    parser.add_argument('--red-sigma', type=float, default=2, help="Number of standard deviations away from the mean for a value to be flagged as a 'red' outlier")
    parser.add_argument('-o', '--output', default="squat", help='Output directory')
    parser.add_argument('--overwrite', action="store_true", default=False, help='If specified, overwrite any existing output')
    parser.add_argument('--generate-test-data', action="store_true", default=False, help='Generate test data')
    parser.add_argument('--generate-test-data-n', type=int, default=10, help='Generate test data for for this number of subjects')
    parser.add_argument('--debug', action="store_true", default=False, help="Enable debug logging")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    _setup_logging(args)
    LOG.info(f"SQUAT: Study-wise QUality Assessment Tool v{__version__}")

    if not args.extract and not args.group_data and not args.generate_test_data:
        raise ValueError("Must specify either --extract or provide a previously extracted group data file with --group-data")
    elif args.extract and args.group_data:
        raise ValueError("Cannot specify --extract and --group-data at the same time")

    if args.group_report or args.subject_reports:
        if not args.report_def:
            raise ValueError("Report definition not given (--report-def)")
        report_def = read_json(args.report_def, "report definition")

    if args.comparison_dists:
        args.comparison_dists = read_json(args.comparison_dists)

    if os.path.exists(args.output) and not args.overwrite:
        raise ValueError(f"Output directory {args.output} already exists - remove or specify a different name")
    os.makedirs(args.output, exist_ok=True)

    if args.extract or args.subject_reports or args.generate_test_data:
        subjids = _get_subjects(args.subjdir, args.subjects)
        subjqcdata = []
        for subjid in subjids:
            subjdir = os.path.join(args.subjdir, subjid)
            subjqcdata.append(SubjectData(
                subjid, subjdir,
                [os.path.join(subjdir, qcpath) for qcpath in args.qcpaths],
            ))

    if args.generate_test_data:
        LOG.info(f'Generating test data for {args.generate_test_data_n} subjects...')
        if len(subjqcdata) == 0:
            raise ValueError("Can't generate test data without a sample subject")
        if len(subjqcdata) != 1:
            LOG.info("WARNING: more than one subject found, will use first subject as base...")
        generate_test_data(args.generate_test_data_n, args.output, subjqcdata[0])
        LOG.info('DONE\n')

    if args.extract:
        LOG.info('Generating group data...')
        group_data = GroupData(subject_datas=subjqcdata)
        group_data.write(os.path.join(args.output, "group_data.json"))
        LOG.info('DONE')
    else:
        group_data = GroupData(fname=args.group_data)

    if args.group_report:
        LOG.info('Generating group QC report...')
        report = Report(report_def, group_data)
        report.save(os.path.join(args.output, "qc_group_report.pdf"))
        LOG.info('DONE')
    
    if args.subject_reports:
        LOG.info('Generating subject QC reports...')
        for subject_data in subjqcdata:
            if args.subject_report_path:
                subjdir = os.path.join(args.subjdir, subject_data.subjid)
                subj_report_path = os.path.join(subjdir, args.subject_report_path)
            else:
                subj_report_path = os.path.join(args.output, f"{subject_data.subjid}_qc_report.pdf")
            LOG.info(f" - {subject_data.subjid}: {subj_report_path}")
            report = Report(report_def, group_data, subject_data, comparison_dists=args.comparison_dists, red_sigma=args.red_sigma, amber_sigma=args.amber_sigma)
            report.save(subj_report_path)
        LOG.info('DONE')

if __name__ == "__main__":
    main()
