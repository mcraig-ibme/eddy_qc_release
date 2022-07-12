"""
SQUAT: Handle operations on the group JSON data file

Matteo Bastiani: FMRIB, Oxford
Martin Craig: SPMIC, Nottingham
"""
import json

class GroupData(dict):

    def __init__(self, fname=None, subject_datas=None):
        if fname is None and subject_datas is None:
            raise ValueError("Must provide filename of existing group data or list of subject data")
        elif fname is not None and subject_datas is not None:
            raise ValueError("Can't provide both filename of existing group data and list of subject data")
        
        if fname is not None:
            self._read_json(fname)
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
        data_fields, group_qc_fields = [], []
        for idx, subject_data in enumerate(subject_datas):
            # Collect list of data fields - anything starting data_
            data_fields = [f for f in subject_data if f.startswith("data_")]

            # Collect list of QC fields - look for any keys starting with qc_<name>
            subject_qc_fields = [f[3:] for f in subject_data if f.startswith("qc_")]
            
            # Check QC fields match for all subjects
            if idx == 0:
                group_qc_fields = subject_qc_fields
                group_qc_data = {k : [] for k in group_qc_fields}
            else:
                for k in subject_qc_fields:
                    if k not in group_qc_fields:
                        raise ValueError(f'Inconsistency in QC fields for subject {idx}: {k} not found in group data')
                for k in group_qc_fields:
                    if k not in subject_qc_fields:
                        raise ValueError(f'Inconsistency in QC fields for subject {idx}: {k} not found in subject data')

            # Collect QC data from subject and add it to the group list
            for qc_field in group_qc_fields:
                subj_qc_data = []
                value = subject_data["qc_" + qc_field]
                if isinstance(value, list):
                    subj_qc_data.extend(value)
                else:
                    subj_qc_data.append(value)
                group_qc_data[qc_field].append(subj_qc_data)
        
        #=========================================================================================
        # Database creation as a dictionary
        #=========================================================================================       
        self.update({
            # data info - note taken from last subject read, assuming consistency
            'data_num_subjects' : len(subject_datas),
            #'data_protocol' : group_qc_data['data'],
        })

        # FIXME assuming data fields match for all subjects and can take from last subject
        # - should check for this
        for data_field in data_fields:
            self[data_field] = subject_data[data_field]

        for qc_field in group_qc_fields:
            self[f"qc_{qc_field}"] = group_qc_data[qc_field]

    def _read_json(self, fname):
        try:
            with open(fname, 'r') as f:
                self.update(json.load(f))
        except (IOError, json.JSONDecodeError) as exc:
            raise ValueError("Could not read group data file: {fname} : {exc}")
