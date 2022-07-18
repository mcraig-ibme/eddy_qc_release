import tempfile
import json
import os

import pytest

from squat.data import GroupData, SubjectData

def test_subjdata_no_data():
    subject_data = SubjectData("sub1")
    assert(len(subject_data.data_fields) == 0)
    assert(len(subject_data.qc_fields) == 0)

def test_subjdata_kwargs():
    subject_data = SubjectData("sub1", qc_test1=3, qc_test2=4.5, data_test1="fish", data_test2="cake", random_test="random")
    assert(subject_data["qc_test1"] == 3)
    assert(subject_data["qc_test2"] == 4.5)
    assert(subject_data["data_test1"] == "fish")
    assert(subject_data["data_test2"] == "cake")
    assert(subject_data["random_test"] == "random")
    assert(len(subject_data.data_fields) == 2)
    assert(len(subject_data.qc_fields) == 2)
    assert("test1" in subject_data.qc_fields)
    assert("test2" in subject_data.qc_fields)
    assert("data_test1" in subject_data.data_fields)
    assert("data_test2" in subject_data.data_fields)

def test_subjdata_load_single():
    data = {
        "data_test1" : "fish",
        "data_test2" : "cake",
        "qc_test1" : 3,
        "qc_test2" : [5, 6],
        "random_test" : "random",
    }
    fname = None
    try:
        f = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        fname = f.name
        json.dump(data, f)
        f.close()
        loaded_data = SubjectData("s1", [fname])
        assert(loaded_data == data)
        assert(len(loaded_data.data_fields) == 2)
        assert(len(loaded_data.qc_fields) == 2)
        assert("test1" in loaded_data.qc_fields)
        assert("test2" in loaded_data.qc_fields)
        assert("data_test1" in loaded_data.data_fields)
        assert("data_test2" in loaded_data.data_fields)
    finally:
        if fname is not None:
            os.remove(fname)

def test_subjdata_load_multiple():
    data1 = {
        "data_test1" : "fish",
        "data_test2" : "cake",
        "qc_test1" : 3,
        "qc_test2" : [5, 6],
        "random_test" : "random",
    }
    data2 = {
        "data_test1" : "dish",
        "data_test3" : "salad",
        "qc_test1" : 4,
        "qc_test3" : 7,
        "random_test" : "random",
    }
    fname1, fname2 = None, None
    try:
        f = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        fname1 = f.name
        json.dump(data1, f)
        f.close()
        f = tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False)
        fname2 = f.name
        json.dump(data2, f)
        f.close()
        loaded_data = SubjectData("s1", [fname1, fname2])
        merged_data = dict(data1)
        merged_data.update(data2)
        assert(loaded_data == merged_data)
        assert(len(loaded_data.data_fields) == 3)
        assert(len(loaded_data.qc_fields) == 3)
        assert("test1" in loaded_data.qc_fields)
        assert("test2" in loaded_data.qc_fields)
        assert("test3" in loaded_data.qc_fields)
        assert("data_test1" in loaded_data.data_fields)
        assert("data_test2" in loaded_data.data_fields)
        assert("data_test3" in loaded_data.data_fields)
    finally:
        if fname1 is not None:
            os.remove(fname1)
        if fname2 is not None:
            os.remove(fname2)

def test_no_input():
    data = GroupData()
    assert(len(data) == 1)
    assert(data["data_num_subjects"] == 0)

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
