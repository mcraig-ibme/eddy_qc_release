import tempfile
import json
import os

import pytest

from squat.data import SubjectData, GroupData
from squat.report import Report

def test_no_report_def():
    with pytest.raises(ValueError):
        report = Report({}, GroupData())
       
def test_empty():
    with pytest.raises(ValueError):
        report = Report({"squat_report" : []}, GroupData())
       
def test_no_data():
    report = Report({"squat_report" : [[{"var" : "qc_test1"}]]}, GroupData())
    fname = None
    try:
        f = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        fname = f.name
        report.save(fname)
    finally:
        if fname is not None:
            os.remove(fname)
