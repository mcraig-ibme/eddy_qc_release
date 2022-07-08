#!/usr/bin/env fslpython
"""
DSQUAD: Handle operations on the group JSON data file

Matteo Bastiani: FMRIB, Oxford
Martin Craig: SPMIC, Nottingham
"""
import json
import os

def main(fn, op, subjects=None):
    """
    Perform a database I/O operation:
    - read from .json file
    - write to .json file
    
    Arguments:
        - fn: Filename of JSON DB to create/read
        - op: 'r' to read, 'w' to write
        - sList: Filename of subject list
    """
    if op == 'w':
        for idx, subject in enumerate(subjects):
            qc_json = os.path.join(subject, 'qc.json')
            if not os.path.isfile(qc_json):
                raise ValueError(qc_json + ' does not appear to be a valid qc.json file')
            with open(qc_json) as qc_file:
                subject_data = json.load(qc_file)
            
            # Collect list of data fields - anything starting data_
            data_fields = [f for f in subject_data if f.startswith("data_")]

            # Collect list of QC fields - look for any keys starting with qc_<name>
            subject_qc_fields = [f[3:] for f in subject_data if f.startswith("qc_")]
            gsquad_report = subject_data.get("gsquad_report", {})
            
            # Check QC fields match for all subjects
            if idx == 0:
                group_qc_fields = subject_qc_fields
                group_qc_data = {k : [] for k in group_qc_fields}
            else:
                if subject_qc_fields != group_qc_fields:
                    raise ValueError(f'Inconsistency in QC fields for subject {idx}: {subject_qc_fields} vs {group_qc_fields}')

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
        db = {
            # data info - note taken from last subject read, assuming consistency
            'data_num_subjects' : len(subjects),
            'gsquad_report' : gsquad_report,
            #'data_protocol' : group_qc_data['data'],
        }

        # FIXME assuming data fields match for all subjects and can take from last subject
        # - should check for this
        for data_field in data_fields:
            db[data_field] = subject_data[data_field]

        for qc_field in group_qc_fields:
            db[f"qc_{qc_field}"] = group_qc_data[qc_field]


        with open(fn, 'w') as fp:
            json.dump(db, fp, sort_keys=True, indent=4, separators=(',', ': '))
    
        return db

    elif op == 'r':
        if not os.path.isfile(fn):
            raise ValueError(fn + ' does not appear to be a valid group_db.json file')
        with open(fn, 'r') as fp:
            return json.load(fp)
