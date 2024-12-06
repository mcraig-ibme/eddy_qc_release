"""
SQUAT: Handle operations on the group JSON data file

Matteo Bastiani: FMRIB, Oxford
Martin Craig: SPMIC, Nottingham
"""
import os
import json
import logging
import math

import numpy as np

LOG = logging.getLogger(__name__)

def read_json(fname, desc):
    try:
        with open(fname, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError) as exc:
        raise IOError(f"Could not read {desc} data file: {fname} : {exc}")

class SubjectData(dict):
    def __init__(self, subjid, subjdir, json_fnames=[], **kwargs):
        dict.__init__(self, **kwargs)
        LOG.debug(f"Subject {subjid} loading from {json_fnames}")
        self.subjid = subjid
        self.subjdir = subjdir
        for fname in json_fnames:
            try:
                self.update(read_json(fname, "subject QC"))
            except IOError as exc:
                LOG.warn(f"Failed to read subject QC data from {fname} - skipping this file")

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
                    self[f] = np.array(self[f], dtype=np.float32).tolist()
                    self.qc_fields.append(f[3:])
                except ValueError:
                    pass # Not numeric data

    def get_image(self, name):
        """
        Get image data for this subject

        :param name: Image name as full path relative to subject directory. Image names can be given 
                     without Nifti or PNG extension.
        :return: Path to matching file or None if not found (warning will be logged)
        """
        fpath = os.path.join(self.subjdir, name)
        extensions = ["", ".nii", ".nii.gz", ".png"]
        for ext in extensions:
            if os.path.isfile(fpath + ext):
                return fpath + ext

        LOG.warn(f"Could not find image for subject {self.subjid} - looking for {name}")
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
            LOG.debug(f"Missing variables for subject {self.subjid} - looking for {var}")
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
            LOG.debug(f"Missing variables in group data - looking for {var}")
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
        # Get QC fields - these may not match for all subjects
        self.qc_fields = set()
        for idx, subject_data in enumerate(subject_datas):
            self.qc_fields.update(subject_data.qc_fields)

        # Collect QC data from subject and add it to the group list. If a QC field is missing
        # for a subject use None
        for idx, subject_data in enumerate(subject_datas):
            for qc_field in self.qc_fields:
                key = f"qc_{qc_field}"
                if key not in self:
                    self[key] = []
                value = subject_data.get(key, None)
                if value is not None and not isinstance(value, list):
                    value = [value]
                self[key].append(value)

        # Get data fields which should match for all subjects
        self.data_fields = set()
        for idx, subject_data in enumerate(subject_datas):
            if idx == 0:
                self.data_fields.update(subject_data.data_fields)
                for k in subject_data.data_fields:
                    self[k] = subject_data[k]
            else:
                for k in subject_data.data_fields:
                    v = subject_data[k]
                    if k not in self:
                        LOG.warn(f"Data field {k} found for subject {subject_data.subjid} but not found in all subjects")
                    elif self[k] != v:
                        LOG.warn(f"Inconsistent value for data field {k} for subject {subject_data.subjid}: {self[k]} vs {v}")
                not_in_subject = [k for k in self.data_fields if k not in subject_data.data_fields]
                if not_in_subject:
                        LOG.warn(f"Data fields {not_in_subject} not found for subject {subject_data.subjid}")

        # Add number of subjects
        self.update({
            'data_num_subjects' : len(subject_datas),
            #'data_protocol' : group_qc_data['data'],
        })

        # Bit messy. We have added None for variables that are missing from a subject, we need to replace this
        # with the correct number of NaN values
        for qc_field in self.qc_fields:
            key = f"qc_{qc_field}"
            subject_values = self[key]
            for idx in range(len(subject_values)):
                if subject_values[idx] is not None:
                    num_values = len(subject_values[idx])
                    break
            for idx in range(len(subject_values)):
                if subject_values[idx] is None:
                    self[key][idx] = [math.nan] * num_values

