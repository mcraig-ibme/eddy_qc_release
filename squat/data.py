"""
SQUAT: Handle operations on the group JSON data file

Matteo Bastiani: FMRIB, Oxford
Martin Craig: SPMIC, Nottingham
"""
import os
import json

import numpy as np

from fsl.data.image import Image

def _check_consistent(subjid, subject_fields, group_fields):
    not_in_group = [k for k in subject_fields if k not in group_fields]
    not_in_subject = [k for k in group_fields if k not in subject_fields]
    if not_in_group:
        raise ValueError(f'Inconsistency in QC fields for subject {subjid}: {not_in_group} not found in group data')
    if not_in_subject:
        raise ValueError(f'Inconsistency in QC fields for subject {subjid}: {not_in_subject} not found in subject data')

def read_json(fname, desc):
    try:
        with open(fname, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as exc:
        raise IOError(f"Could not read {desc} data file: {fname} : {exc}")

class SubjectData(dict):
    def __init__(self, subjid, json_fnames=[], img_fnames=[], **kwargs):
        dict.__init__(self, **kwargs)
        self.subjid = subjid
        for fname in fnames:
            try:
                self.update(read_json(fname, "subject QC"))
            except IOError as exc:
                print(f"WARNING: Failed to read subject QC data from {fname} - skipping this file")
        self["_imgs"] = img_fnames

        # Collect list of data fields - anything starting data_
        self.data_fields = [f for f in self if f.startswith("data_")]

        # Collect list of QC fields - look for any keys starting with qc_<name>
        # containing numeric data FIXME super-ugly
        self.qc_fields = []
        for f in self:
            if not f.startswith("qc_"):
                continue
            elif isinstance(self[f], (int, float)) and not isinstance(self[f], bool):
                self.qc_fields.append(f[3:])
            elif isinstance(self[f], list):
                try:
                    self[f] = [float(v) for v in self[f]]
                    self.qc_fields.append(f[3:])
                except ValueError:
                    pass # Not numeric data

    def get_image(self, name):
        """
        Get image data for this subject

        :param name: Image name. Can be a full path relative to subject directory, or simply a filename
                     in which case the first matching file in the list will be returned. Generally it's
                     better if QC images all have distinct filenames. Image names should be given without
                     Nifti extension and are compared in a case-insensitive way.
        :return: Path to the named data or None if not found (warning will be logged)
        """
        if ".nii" in name:
            name = name[:name.index(".nii")]

        for fpath in self["_imgs"]:
            if fpath.strip().lower() == name.strip().lower():
                return fpath
        for fpath in self["_imgs"]:
            fname = os.path.basename(fpath)
            if fname.strip().lower() == name.strip().lower():
                return fpath
        print(f"WARNING: Could not find image for subject {self.subjid} - looking for {name}")
        return None

    def get_data(self, var):
        """
        Get data values for this subject

        :param vars: Name of QC variable (without the qc_ prefix) or list of variable names
        :return: 1D Numpy array of values, empty if any of the variables could not be found
        """
        try:
            return np.atleast_1d(self['qc_' + var])
        except KeyError:
            print(f"WARNING: Missing variables for subject {self.subjid} - looking for {var}")
            return np.atleast_1d([])

class GroupData(dict):
    def __init__(self, fname=None, subject_datas=[]):
        dict.__init__(self)
        if fname and subject_datas:
            raise ValueError("Can't provide both filename of existing group data and list of subject data")

        self._read_subject_data(subject_datas)
        if fname:
            self.update(read_json(fname, "group"))

    def get_data(self, var):
        """
        Get group data values

        :param vars: Name of QC variable (without the qc_ prefix) or list of variable names
        :return: 2D Numpy array of values shape [NSUBJS, NVALS], empty if any of the variables could not be found
        """
        try:
            return np.atleast_2d(self['qc_' + var])
        except KeyError:
            print(f"WARNING: Missing variables in group data - looking for {var}")
            return np.atleast_2d([])

    def write(self, fname):
        """
        Write group data to JSON file
        """
        with open(fname, 'w') as f:
            json.dump(self, f, sort_keys=True, indent=4, separators=(',', ': '))

    def _read_subject_data(self, subject_datas):
        """
        Read single-subject QC data and combine it into group data

        :param subject_datas: Sequence of single subject QC data dictionaries
        """
        self.data_fields, self.qc_fields = [], []
        for idx, subject_data in enumerate(subject_datas):
            # Check QC and data fields match for all subjects
            if idx == 0:
                self.qc_fields = subject_data.qc_fields
                self.data_fields = subject_data.data_fields
                group_qc_data = {k : [] for k in self.qc_fields}
            else:
                _check_consistent(subject_data.subjid, subject_data.qc_fields, self.qc_fields)
                _check_consistent(subject_data.subjid, subject_data.data_fields, self.data_fields)

            # Collect QC data from subject and add it to the group list
            for qc_field in self.qc_fields:
                subj_qc_data = []
                value = subject_data["qc_" + qc_field]
                if isinstance(value, list):
                    subj_qc_data.extend(value)
                else:
                    subj_qc_data.append(value)
                group_qc_data[qc_field].append(subj_qc_data)
        
        # Update dictionary to include group data and QC fields  
        self.update({
            'data_num_subjects' : len(subject_datas),
            #'data_protocol' : group_qc_data['data'],
        })

        # FIXME assuming data fields match for all subjects and can take from last subject
        # - should check for this
        for data_field in self.data_fields:
            self[data_field] = subject_data[data_field]

        for qc_field in self.qc_fields:
            self[f"qc_{qc_field}"] = group_qc_data[qc_field]
