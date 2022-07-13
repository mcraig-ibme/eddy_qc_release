import tempfile
import json
import os

import pytest

from squat.data import GroupData, SubjectData

def test_no_input_exc():
    with pytest.raises(ValueError):
        data = GroupData()
       
def test_file_and_subjdata_exc():
    with pytest.raises(ValueError):
        data = GroupData(fname="fish", subject_datas=[])

def test_empty():
    data = GroupData(subject_datas=[])
    assert(len(data) == 1)
    assert(data["data_num_subjects"] == 0)

def test_one_subject():
    subject_data = SubjectData("sub1", qc_test1=3, qc_test2=4.5)
    data = GroupData(subject_datas=[subject_data])
    assert(len(data) == 3)
    assert(data["data_num_subjects"] == 1)
    assert(data["qc_test1"] == [[3]])
    assert(data["qc_test2"] == [[4.5]])

def test_two_subjects():
    subject_data1 = SubjectData("sub1", qc_test1=3, qc_test2=4.5)
    subject_data2 = SubjectData("sub2", qc_test1=3.1, qc_test2=4.6)
    data = GroupData(subject_datas=[subject_data1, subject_data2])
    assert(len(data) == 3)
    assert(data["data_num_subjects"] == 2)
    assert(data["qc_test1"] == [[3], [3.1]])
    assert(data["qc_test2"] == [[4.5], [4.6]])

def test_multiple_values():
    subject_data1 = SubjectData("sub1", qc_test1=[3, 4])
    subject_data2 = SubjectData("sub2", qc_test1=[5, 6])
    data = GroupData(subject_datas=[subject_data1, subject_data2])
    assert(len(data) == 2)
    assert(data["data_num_subjects"] == 2)
    assert(data["qc_test1"] == [[3, 4], [5, 6]])

def test_data():
    subject_data1 = SubjectData("sub1", data_test1="Test data")
    subject_data2 = SubjectData("sub2", data_test1="Test data")
    data = GroupData(subject_datas=[subject_data1, subject_data2])
    assert(len(data) == 2)
    assert(data["data_num_subjects"] == 2)
    assert(data["data_test1"] == "Test data")

def test_data_inconsistent_fields():
    subject_data1 = SubjectData("sub1", data_test1="Test data")
    subject_data2 = SubjectData("sub2", data_test2="Test data")
    with pytest.raises(ValueError):
        data = GroupData(subject_datas=[subject_data1, subject_data2])

@pytest.mark.skip("Data consistency not yet enforced")
def test_data_inconsistent_content():
    subject_data1 = SubjectData("sub1", data_test1="Test data")
    subject_data2 = SubjectData("sub2", data_test1="Different test data")
    with pytest.raises(ValueError):
        data = GroupData(subject_datas=[subject_data1, subject_data2])

def test_inconsistant_qc():
    subject_data1 = SubjectData("sub1", qc_test1=3)
    subject_data2 = SubjectData("sub2", qc_test2=4.6)
    with pytest.raises(ValueError):
        data = GroupData(subject_datas=[subject_data1, subject_data2])

def test_inconsistant_qc_missing():
    subject_data1 = SubjectData("sub1", qc_test1=3)
    subject_data2 = SubjectData("sub2", qc_test1=3.1, qc_test2=4.6)
    with pytest.raises(ValueError):
        data = GroupData(subject_datas=[subject_data1, subject_data2])

def test_load():
    data = {
        "data_num_subjects" : 2,
        "data_test1" : "Test data",
        "qc_test1" : [[3], [4]],
        "qc_test2" : [[5, 6], [7, 8]],
    }
    fname = None
    try:
        f = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        fname = f.name
        json.dump(data, f)
        f.close()
        loaded_data = GroupData(fname=fname)
        assert(loaded_data == data)
    finally:
        if fname is not None:
            os.remove(fname)
