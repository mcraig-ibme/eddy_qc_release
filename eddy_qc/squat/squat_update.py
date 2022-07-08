#!/usr/bin/env fslpython
"""
SQUAT - Update single subject pdfs

Matteo Bastiani, FMRIB, Oxford
Martin Craig, SPMIC, Nottingham
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import seaborn
import os
import json
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from eddy_qc.squat import squat_group
from eddy_qc.squat import squat_var
from eddy_qc.QUAD import quad_tables
from eddy_qc.utils import ref_page
seaborn.set()

def main(db, sList, grp, grpDb):
    """
    Update the single subject SQUAT reports by:
    - replacing first page with tables with coulour-coded cells indicating performances agains the database
    - adding the single subject performance as white star against the whole population and, if specified, against the subject's group
    
    Arguments:
        - db: qc pdf file
        - sList: list of single subject squat folders
        - grp: Optional grouping variable
        - grpDb: group data
    """
    # Define thresholds to check for outliers
    # To avoid dividing by 0 in the colour indexing, added 1e-10 
    thresholds = {}
    for key, value in db.items():
        if key.startswith("qc_"):
            thresholds[key] = {}
            thresholds[key]["avg"] = np.mean(value, axis=0) + 1e-10
            thresholds[key]["std"] = np.std(value, axis=0) + 1e-10

    # Colormap to mark outliers in the summary tables
    colours = np.array([[0.18, 0.79, 0.22, 0.5], [0.91, 0.71, 0.09, 0.5], [0.8, 0.20, 0.20, 0.5], [0, 0, 0, 0]])

    if (grp is True and 
        grpDb is False):            
        print('Database and listed subjects have different grouping variable.')

    with open(sList) as fp:
        subjects = [l.strip() for l in fp.readlines()]

    for s_idx, subject in enumerate(subjects):
        qc_pdf = subject + '/qc.pdf'
        if not os.path.isfile(qc_pdf):
            raise ValueError(qc_pdf + ' does not appear to be a valid qc.pdf file')
        qc_json = subject + '/qc.json'
        if not os.path.isfile(qc_json):
            raise ValueError(qc_json + ' does not appear to be a valid qc.json file')
        else:
            with open(qc_json) as qc_file:    
                sData = json.load(qc_file)

        # Get colormap indices based on the level of outlier
        for qc_var, threshold in thresholds.items():
            zval = (sData[qc_var], sData['qc_mot_rel']-threshold["avg"])/threshold["std"]
            colour_idx = np.clip(np.floor(np.abs(zval), 0, 2)).astype(int)

        b_db = (np.array(db['data_unique_bvals'])).reshape(-1,1)
        b_sub = (np.array(sData['data_unique_bvals'])).reshape(-1,1)
        common_b = np.array(np.all((np.abs(b_db[:,None,:]-b_sub[None,:,:])<100),axis=-1).nonzero()).T
        pe_db = np.reshape(np.atleast_2d(db['data_unique_pes']), (-1,4))[:,0:3]
        pe_sub = np.reshape(np.atleast_2d(sData['data_eddy_para']), (-1,4))[:,0:3]
        common_pe = np.array(np.all((pe_db[:,None,:]==pe_sub[None,:,:]),axis=-1).nonzero()).T

        ol_colour_idx = (3*np.ones(1+sData['data_no_shells']+sData['data_no_PE_dirs'])).astype(int)     
        if sData['qc_ol_flag']:
            ol_colour_idx[0] = (np.clip(np.floor((sData['qc_outliers_tot']-ol_avg[0])/ol_std[0]),0,2)).astype(int)    
            ol_colour_idx[1:][(common_b[:,1])] = (np.clip(np.floor((np.array(sData['qc_outliers_b'])[common_b[:,1]]-ol_avg[1+common_b[:,0]])/ol_std[1+common_b[:,0]]),0,2)).astype(int)    
            ol_colour_idx[1+sData['data_no_shells']:][(common_pe[:,1])] = (np.clip(np.floor((np.array(sData['qc_outliers_pe'])[common_pe[:,1]]-ol_avg[1+sData['data_no_shells']+common_pe[:,0]])/ol_std[1+sData['data_no_shells']+common_pe[:,0]]),0,2)).astype(int)    
            
        cnr_colour_idx = (3*np.ones(1+sData['data_no_shells'])).astype(int)
        if sData['qc_cnr_flag']:
            cnr_colour_idx[0] = (np.abs(np.clip(np.ceil((sData['qc_cnr_avg'][0]-cnr_avg[0])/cnr_std[0]),-2,0))).astype(int)    
            cnr_colour_idx[1:][(common_b[:,1])] = (np.abs(np.clip(np.ceil((np.array(sData['qc_cnr_avg'])[1+common_b[:,1]]-cnr_avg[1+common_b[:,0]])/cnr_std[1+common_b[:,0]]),-2,0))).astype(int)    
        
        # Fill eddy and data dictionaries for squat_tables function
        eddy = {
        'motionFlag':True,
        'avg_abs_mot':sData['qc_mot_abs'],
        'avg_rel_mot':sData['qc_mot_rel'],
        'mot_colour':colours[mot_colour_idx],

        'paramsFlag':sData['qc_params_flag'],
        'avg_params':sData['qc_params_avg'],
        'params_colour':colours[np.concatenate((par_colour_idx, ec_colour_idx))],
        
        's2vFlag':sData['qc_s2v_params_flag'],
        'avg_std_s2v_params':sData['qc_s2v_params_avg_std'],
        's2v_params_colour':colours[s2v_par_colour_idx],
        
        'fieldFlag':sData['qc_field_flag'],
        'std_displacement':sData['qc_vox_displ_std'],
        'field_colour':colours[susc_colour_idx],

        'olFlag':sData['qc_ol_flag'],
        'tot_ol':sData['qc_outliers_tot'],
        'b_ol':sData['qc_outliers_b'],
        'pe_ol':sData['qc_outliers_pe'],
        'ol_colour':colours[ol_colour_idx],

        'cnrFlag':sData['qc_cnr_flag'],
        'avg_cnr':sData['qc_cnr_avg'],
        'cnr_colour':colours[cnr_colour_idx],
        }   
        data = {
        'subj_id':sData['data_file_eddy'],
        'qc_path':subject,
        'unique_bvals':np.array(sData['data_unique_bvals']),
        'unique_pedirs':np.array(sData['data_unique_pes']),
        'eddy_para':np.array(sData['data_eddy_para']),
        }

        # Generate a new single subject summary table pdf with outlier colour coding
        pp = PdfPages(subject + '/qc_tables_tmp.pdf')        
        ref_page.main(pp, data, [])     
        quad_tables.main(pp, data, eddy, True)
        pp.close()
        
        # Generate a new group pdf with subject marked as white star
        pp = PdfPages(subject + '/qc_tmp.pdf')   
        squat_report.main(pp, db, grp, sData)
        if grp is not False:
            if grpDb is False:
                squat_var.main(pp, db, grp, sData, grp[grp.dtype.names[0]][s_idx+1])
            else:
                squat_var.main(pp, db, grpDb, sData, grp[grp.dtype.names[0]][s_idx+1])
        pp.close()
        
        # Merge the three pdfs
        file1 = PdfFileReader(subject + '/qc_tables_tmp.pdf', 'rb')
        file2 = PdfFileReader(subject + '/qc.pdf', 'rb')
        file3 = PdfFileReader(subject + '/qc_tmp.pdf', 'rb')

        output = PdfFileWriter()

        for i in np.arange(0, file1.numPages):
            output.addPage(file1.getPage(i))
        # Get pages from quad report and skip ref page if present
        if os.path.isfile(subject + '/ref.txt'):
            i_start = 2
        else:
            i_start = 1
        for i in np.arange(i_start, file2.numPages):
            output.addPage(file2.getPage(i))
        for i in np.arange(0, file3.numPages):
            output.addPage(file3.getPage(i))

        outputStream = open(subject + '/qc_updated.pdf', 'wb')
        output.write(outputStream)
        outputStream.close()
        
        # Clear temporary pdf files
        os.remove(subject + '/qc_tables_tmp.pdf')
        os.remove(subject + '/qc_tmp.pdf')
