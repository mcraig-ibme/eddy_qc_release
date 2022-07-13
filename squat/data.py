"""
SQUAT: Handle operations on the group JSON data file

Matteo Bastiani: FMRIB, Oxford
Martin Craig: SPMIC, Nottingham
"""
import json

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
        raise ValueError(f"Could not read {desc} data file: {fname} : {exc}")

class SubjectData(dict):
    def __init__(self, subjid, fname=None, **kwargs):
        dict.__init__(self, **kwargs)
        self.subjid = subjid
        if fname:
            self.update(read_json(fname, "subject QC"))
    
        # Collect list of data fields - anything starting data_
        self.data_fields = [f for f in self if f.startswith("data_")]

        # Collect list of QC fields - look for any keys starting with qc_<name>
        self.qc_fields = [f[3:] for f in self if f.startswith("qc_")]

class GroupData(dict):
    def __init__(self, fname=None, subject_datas=None):
        dict.__init__(self)
        if fname is None and subject_datas is None:
            raise ValueError("Must provide filename of existing group data or list of subject data")
        elif fname is not None and subject_datas is not None:
            raise ValueError("Can't provide both filename of existing group data and list of subject data")
        
        if fname is not None:
            self.update(read_json(fname, "group"))
        else:
            self._read_subject_data(subject_datas)

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
        group_data_fields, group_qc_fields = [], []
        for idx, subject_data in enumerate(subject_datas):
            # Check QC fields match for all subjects
            if idx == 0:
                group_qc_fields = subject_data.qc_fields
                group_data_fields = subject_data.data_fields
                group_qc_data = {k : [] for k in group_qc_fields}
            else:
                _check_consistent(subject_data.subjid, subject_data.qc_fields, group_qc_fields)
                _check_consistent(subject_data.subjid, subject_data.data_fields, group_data_fields)

            # Collect QC data from subject and add it to the group list
            for qc_field in group_qc_fields:
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
        for data_field in group_data_fields:
            self[data_field] = subject_data[data_field]

        for qc_field in group_qc_fields:
            self[f"qc_{qc_field}"] = group_qc_data[qc_field]
