#!/usr/bin/env fslpython

import json










#=========================================================================================
# QUAD - Export data and qc indices to JSON file 
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================


def main(data, eddy, eddy_input):
    """
    Create JSON file that contains data informationa and qc indices derived from the single
    subject qc analysis. This information will then be used for a further group qc analysis
    (if needed).
    
    Arguments:
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
    """
    
    data_json = {
        'eddy_input_flag':eddy_input.KnowsParameters(),
        'eddy_input':eddy_input.GetParameters(),
        
        'data_file_eddy':data['subj_id'],
        'data_file_mask':data['mask_id'],
        'data_file_bvals':data['bvals_id'],
        'data_no_dw_vols':data['no_dw_vols'].tolist(),
        'data_no_b0_vols':data['no_b0_vols'].tolist(),
        'data_no_PE_dirs':data['no_PE_dirs'],
        'data_protocol':data['protocol'].tolist(),
        'data_no_shells':data['no_shells'].tolist(),
        'data_unique_bvals':data['unique_bvals'].tolist(),
        'data_unique_pes':data['unique_pedirs'].tolist(),
        'data_eddy_para':data['eddy_para'].tolist(),
        'data_vox_size':data['vox_size'][0:3].tolist(),

        'qc_path':data['qc_path'],
        'qc_mot_abs':round(eddy['avg_abs_mot'], 2),
        'qc_mot_rel':round(eddy['avg_rel_mot'], 2),
        'qc_params_flag':eddy['paramsFlag'],
        'qc_params_avg':eddy['avg_params'].tolist(),
        'qc_s2v_params_flag':eddy['s2vFlag'],
        'qc_s2v_params_avg_std':eddy['avg_std_s2v_params'].tolist(),
        'qc_field_flag':eddy['fieldFlag'],
        'qc_vox_displ_std':eddy['std_displacement'].tolist(),
        'qc_ol_flag':eddy['olFlag'],
        'qc_outliers_tot':eddy['tot_ol'],
        'qc_outliers_b':eddy['b_ol'].tolist(),
        'qc_outliers_pe':eddy['pe_ol'].tolist(),
        'qc_cnr_flag':eddy['cnrFlag'],
        'qc_cnr_avg':eddy['avg_cnr'].tolist(),
        'qc_cnr_std':eddy['std_cnr'].tolist(),
        'qc_rss_flag':eddy['rssFlag'],
    }

    # Write dictionary to json
    with open(data['qc_path'] + '/qc.json', 'w') as fp:
        json.dump(data_json, fp, sort_keys=True, indent=4, separators=(',', ': '))
    

    
           
