#!/usr/bin/env fslpython

import json
import os

#=========================================================================================
# SQUAD - Perform database I/O operations
# Matteo Bastiani
# 01-08-2017, FMRIB, Oxford
#=========================================================================================

# Names of JSON fields which flag whether a particular QC output is relevant
QC_FLAG_FIELDS = {
    'ol' : 'qc_ol_flag', 
    'susc' : 'qc_field_flag', 
    'par' : 'qc_params_flag', 
    's2v_par' : 'qc_s2v_params_flag', 
    'cnr' : 'qc_cnr_flag', 
    'rss' : 'qc_rss_flag',
}

# Names of JSON fields containing data for each QC output
QC_DATA_FIELDS = {
    'ol' : ['qc_outliers_tot', 'qc_outliers_b', 'qc_outliers_pe'],
    'susc' : ['qc_vox_displ_std'],
    'par' : ['qc_params_avg'],
    's2v_par' : ['qc_s2v_params_avg_std'],
    'cnr' :  ['qc_cnr_avg'],
    'motion' : ['qc_mot_abs', 'qc_mot_rel'],
    'data' : ['data_protocol'],
}

# Names of JSON fields containing acquisition/parameter information
# (taken from last subject read and assumed to match for all)
ACQ_DATA_FIELDS = {
    'data_no_shells' : 'data_no_shells',
    'data_no_pes' : 'data_no_PE_dirs',
    'data_no_b0_vols' : 'data_no_b0_vols',
    'data_no_dw_vols' : 'data_no_dw_vols',
    'data_unique_bvals' : 'data_unique_bvals',
    'data_unique_pes' : 'data_eddy_para',
    'data_vox_size' : 'data_vox_size',
}

def main(fn, op, sList):
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
        with open(sList) as fp:
            subjects = [l.strip() for l in fp.readlines()]
        
        group_qc_data = {k : [] for k in QC_DATA_FIELDS}

        for idx, subject in enumerate(subjects):
            qc_json = os.path.join(subject, 'qc.json')
            if not os.path.isfile(qc_json):
                raise ValueError(qc_json + ' does not appear to be a valid qc.json file')
            with open(qc_json) as qc_file:    
                sData = json.load(qc_file)

            # Check that eddy has been run in the same way for all subjects
            subject_flag_values = {key : sData.get(field, False) for key, field in QC_FLAG_FIELDS.items()}
            if idx == 0:
                group_flag_values = subject_flag_values
            else:
                if subject_flag_values != group_flag_values:
                    raise ValueError('Eddy output inconsistency detected!')

            # Collect QC data from subject and add it to the group list
            subj_qc_data = {k : [] for k in QC_DATA_FIELDS.keys()}
            for key, fields in QC_DATA_FIELDS.items():
                subj_qc_data = []
                if group_flag_values.get(key, True):
                    for field in fields:
                        if field in sData:
                            value = sData[field]
                            if isinstance(value, list):
                                subj_qc_data.extend(value)
                            else:
                                subj_qc_data.append(value)
                group_qc_data[key].append(subj_qc_data)
        
        #=========================================================================================
        # Database creation as a dictionary
        #
        # FIXME use naming conventions to simplify this
        #=========================================================================================       
        db = {
            # data info - note taken from last subject read, assuming consistency
            'data_no_subjects' : len(subjects),
            'data_protocol' : group_qc_data['data'],

            # qc indices
            'qc_motion' : group_qc_data['motion'],
            'qc_parameters' : group_qc_data['par'],
            'qc_s2v_parameters' : group_qc_data['s2v_par'],
            'qc_susceptibility' : group_qc_data['susc'],
            'qc_outliers' : group_qc_data['ol'],
            'qc_cnr' : group_qc_data['cnr'],
        }
        for key, field in ACQ_DATA_FIELDS.items():
            db[key] = sData[field]

        # eddy options
        for key in group_flag_values:
            db[key + '_flag'] = group_flag_values[key]

        with open(fn, 'w') as fp:
            json.dump(db, fp, sort_keys=True, indent=4, separators=(',', ': '))
    
        return db

    elif op == 'r':
        if not os.path.isfile(fn):
            raise ValueError(fn + ' does not appear to be a valid group_db.json file')
        with open(fn, 'r') as fp:
            return json.load(fp)
