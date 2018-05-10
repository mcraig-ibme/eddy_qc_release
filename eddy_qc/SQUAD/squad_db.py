#!/usr/bin/env fslpython

import json
import os




#=========================================================================================
# SQUAD - Perform database I/O operations
# Matteo Bastiani
# 01-08-2017, FMRIB, Oxford
#=========================================================================================

def main(fn, op, sList):
    """
    Perform a database I/O operation:
    - read from .json file
    - write to .json file
    
    Arguments:
        - db: database in dictionary format
        - fn: filename
        - op: 'r' to read, 'w' to write
    """
    if op == 'w':
        
        countSubjects = 0
        data_list = []
        qc_mot_list = []
        qc_params_list = []
        qc_s2v_params_list = []
        qc_susc_list = []
        qc_ol_list = []
        qc_cnr_list = []
        
        with open(sList) as fp:
            for line in fp:
                line=line.rstrip('\n')
                qc_json = line + '/qc.json'
                if not os.path.isfile(qc_json):
                    raise ValueError(qc_json + ' does not appear to be a valid qc.json file')
                countSubjects = countSubjects + 1
                with open(qc_json) as qc_file:    
                    sData = json.load(qc_file)
                # Check that eddy has been run in the same way for all subjects
                if countSubjects == 1:
                    ol_flag = sData['qc_ol_flag']
                    susc_flag = sData['qc_field_flag']
                    par_flag = sData['qc_params_flag']
                    s2v_par_flag = sData['qc_s2v_params_flag']
                    cnr_flag = sData['qc_cnr_flag']
                    rss_flag = sData['qc_rss_flag']
                else:
                    if sData['qc_params_flag'] != par_flag:
                        raise ValueError('Eddy output inconsistency detected!')
                    if sData['qc_s2v_params_flag'] != s2v_par_flag:
                        raise ValueError('Eddy output inconsistency detected!')
                    if sData['qc_field_flag'] != susc_flag:
                        raise ValueError('Eddy output inconsistency detected!')
                    if sData['qc_ol_flag'] != ol_flag:
                        raise ValueError('Eddy output inconsistency detected!')
                    if sData['qc_cnr_flag'] != cnr_flag:
                        raise ValueError('Eddy output inconsistency detected!')
                    if sData['qc_rss_flag'] != rss_flag:
                        raise ValueError('Eddy output inconsistency detected!')
        

                # Initialize empty subject lists
                data_tmp = []
                mot_tmp = []
                par_tmp = []
                s2v_par_tmp = []
                susc_tmp = []
                ol_tmp = []
                cnr_tmp = []    

                # Store qc indices in lists
                data_tmp.extend(sData['data_protocol'])
                
                mot_tmp.extend([sData['qc_mot_abs'], sData['qc_mot_rel']])
                if sData['qc_params_flag']:
                    par_tmp.extend(sData['qc_params_avg'])
                if sData['qc_s2v_params_flag']:
                    s2v_par_tmp.extend(sData['qc_s2v_params_avg_std'])
                if sData['qc_field_flag']:
                    susc_tmp.append(sData['qc_vox_displ_std'])
                if sData['qc_ol_flag']:
                    ol_tmp.append(sData['qc_outliers_tot'])
                    ol_tmp.extend(sData['qc_outliers_b'])
                    ol_tmp.extend(sData['qc_outliers_pe'])
                if sData['qc_cnr_flag']:
                    cnr_tmp.extend(sData['qc_cnr_avg'])
                
                data_list.append(data_tmp)
                qc_mot_list.append(mot_tmp)
                qc_params_list.append(par_tmp)
                qc_s2v_params_list.append(s2v_par_tmp)
                qc_susc_list.append(susc_tmp)
                qc_ol_list.append(ol_tmp)
                qc_cnr_list.append(cnr_tmp)
        
        
        #=========================================================================================
        # Database creation as a dictionary
        #=========================================================================================       
        db = {
            # eddy options
            'ol_flag':ol_flag,
            'par_flag':par_flag,
            's2v_par_flag':s2v_par_flag,
            'susc_flag':susc_flag,
            'cnr_flag':cnr_flag,
            'rss_flag':rss_flag,

            # data info
            'data_no_subjects':countSubjects,
            'data_no_shells':sData['data_no_shells'],
            'data_no_pes':sData['data_no_PE_dirs'],
            'data_no_b0_vols':sData['data_no_b0_vols'],
            'data_no_dw_vols':sData['data_no_dw_vols'],
            'data_unique_bvals':sData['data_unique_bvals'],
            'data_unique_pes':sData['data_eddy_para'],
            'data_protocol':data_list,
            'data_vox_size':sData['data_vox_size'],

            # qc indices
            'qc_motion':qc_mot_list,
            'qc_parameters':qc_params_list,
            'qc_s2v_parameters':qc_s2v_params_list,
            'qc_susceptibility':qc_susc_list,
            'qc_outliers':qc_ol_list,
            'qc_cnr':qc_cnr_list,
        }

        with open(fn, 'w') as fp:
            json.dump(db, fp, sort_keys=True, indent=4, separators=(',', ': '))
    
        return db

    elif op == 'r':
        if not os.path.isfile(fn):
            raise ValueError(fn + ' does not appear to be a valid group_db.json file')
        with open(fn, 'r') as fp:
            return json.load(fp)
    