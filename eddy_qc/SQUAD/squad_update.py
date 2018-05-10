#!/usr/bin/env fslpython

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_pdf import PdfPages
import seaborn
import os
import json
from PyPDF2 import PdfFileMerger, PdfFileReader, PdfFileWriter
from eddy_qc.SQUAD import squad_group
from eddy_qc.SQUAD import squad_var
from eddy_qc.QUAD import quad_tables
seaborn.set()






#=========================================================================================
# SQUAD - Update single subject pdfs
# Matteo Bastiani
# 01-08-2017, FMRIB, Oxford
#=========================================================================================

def main(db, sList, grp, grpDb):
    """
    Update the single subject SQUAD reports by:
    - replacing first page with tables with coulour-coded cells indicating performances agains the database
    - adding the single subject performance as white star against the whole population and, if specified, against the subject's group
    
    Arguments:
        - db: qc pdf file
        - sList: list of single subject squad folders
        - grp: grouping variable
    """
    # Define thresholds to check for outliers
    # To avoid dividing by 0 in the colour indexing, added 1e-10 
    mot_avg = np.mean(db['qc_motion'], axis=0) + 0.0000000001
    mot_std = np.std(db['qc_motion'], axis=0) + 0.0000000001
    
    par_avg = np.mean(db['qc_parameters'], axis=0) + 0.0000000001
    par_std = np.std(db['qc_parameters'], axis=0) + 0.0000000001
    
    s2v_par_avg = np.mean(db['qc_s2v_parameters'], axis=0) + 0.0000000001
    s2v_par_std = np.std(db['qc_s2v_parameters'], axis=0) + 0.0000000001
    
    susc_avg = np.mean(db['qc_susceptibility'], axis=0) + 0.0000000001
    susc_std = np.std(db['qc_susceptibility'], axis=0) + 0.0000000001
    
    ol_avg = np.mean(db['qc_outliers'], axis=0) + 0.0000000001
    ol_std = np.std(db['qc_outliers'], axis=0) + 0.0000000001
    
    cnr_avg = np.mean(db['qc_cnr'], axis=0) + 0.0000000001
    cnr_std = np.std(db['qc_cnr'], axis=0) + 0.0000000001

    # Colormap to mark outliers in the summary tables
    colours = np.array([[0.18, 0.79, 0.22, 0.5], [0.91, 0.71, 0.09, 0.5], [0.8, 0.20, 0.20, 0.5], [0, 0, 0, 0]])
    
    # Colormap to mark outliers in the summary tables
    if (grp is True and 
        grpDb is False):            
        print('Database and listed subjects have different grouping variable.')
    
    s_idx = 0
    with open(sList) as fp:
        for line in fp:
            line=line.rstrip('\n')
            qc_pdf = line + '/qc.pdf'
            if not os.path.isfile(qc_pdf):
                raise ValueError(qc_pdf + ' does not appear to be a valid qc.pdf file')
            qc_json = line + '/qc.json'
            if not os.path.isfile(qc_json):
                raise ValueError(qc_json + ' does not appear to be a valid qc.json file')
            else:
                with open(qc_json) as qc_file:    
                    sData = json.load(qc_file)
            
            # Get colormap indices based on the level of outlier
            mot_colour_idx = (np.clip(np.floor(((sData['qc_mot_abs'], sData['qc_mot_rel'])-mot_avg)/mot_std),0,2)).astype(int)
            par_colour_idx = (np.clip(np.floor(np.abs((sData['qc_params_avg'][0:6]-par_avg[0:6])/par_std[0:6])),0,2)).astype(int)
            s2v_par_colour_idx = (np.clip(np.floor((sData['qc_s2v_params_avg_std']-s2v_par_avg)/s2v_par_std),0,2)).astype(int)
            ec_colour_idx = (np.clip(np.floor(((sData['qc_params_avg'][6:9]-par_avg[6:9])/par_std[6:9])),0,2)).astype(int)
            susc_colour_idx = (np.clip(np.floor((sData['qc_vox_displ_std']-susc_avg)/susc_std),0,2)).astype(int)

            b_db = (np.array(db['data_unique_bvals'])).reshape(-1,1)
            b_sub = (np.array(sData['data_unique_bvals'])).reshape(-1,1)
            common_b = np.array(np.all((np.abs(b_db[:,None,:]-b_sub[None,:,:])<100),axis=-1).nonzero()).T
            pe_db = np.reshape(np.atleast_2d(db['data_unique_pes']), (-1,4))[:,0:3]
            pe_sub = np.reshape(np.atleast_2d(sData['data_eddy_para']), (-1,4))[:,0:3]
            common_pe = np.array(np.all((pe_db[:,None,:]==pe_sub[None,:,:]),axis=-1).nonzero()).T
            
            ol_colour_idx = (3*np.ones(1+sData['data_no_shells']+sData['data_no_PE_dirs'])).astype(int)       
            ol_colour_idx[0] = (np.clip(np.floor((sData['qc_outliers_tot']-ol_avg[0])/ol_std[0]),0,2)).astype(int)    
            ol_colour_idx[1:][(common_b[:,1])] = (np.clip(np.floor((np.array(sData['qc_outliers_b'])[common_b[:,1]]-ol_avg[1+common_b[:,0]])/ol_std[1+common_b[:,0]]),0,2)).astype(int)    
            ol_colour_idx[1+sData['data_no_shells']:][(common_pe[:,1])] = (np.clip(np.floor((np.array(sData['qc_outliers_pe'])[common_pe[:,1]]-ol_avg[1+sData['data_no_shells']+common_pe[:,0]])/ol_std[1+sData['data_no_shells']+common_pe[:,0]]),0,2)).astype(int)    
            
            cnr_colour_idx = (3*np.ones(1+sData['data_no_shells'])).astype(int)       
            cnr_colour_idx[0] = (np.abs(np.clip(np.ceil((sData['qc_cnr_avg'][0]-cnr_avg[0])/cnr_std[0]),-2,0))).astype(int)    
            cnr_colour_idx[1:][(common_b[:,1])] = (np.abs(np.clip(np.ceil((np.array(sData['qc_cnr_avg'])[1+common_b[:,1]]-cnr_avg[1+common_b[:,0]])/cnr_std[1+common_b[:,0]]),-2,0))).astype(int)    
            
            # Fill eddy and data dictionaries for squad_tables function
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
            'unique_bvals':np.array(sData['data_unique_bvals']),
            'unique_pedirs':np.array(sData['data_unique_pes']),
            'eddy_para':np.array(sData['data_eddy_para']),
            }

            # Generate a new single subject summary table pdf with outlier colour coding
            pp = PdfPages(line + '/qc_tables_tmp.pdf')        
            quad_tables.main(pp, data, eddy, True)
            pp.close()
            
            # Generate a new group pdf with subject marked as white star
            pp = PdfPages(line + '/qc_tmp.pdf')        
            squad_group.main(pp, db, grp, sData)
            if grp is not False:
                if grpDb is False:
                    squad_var.main(pp, db, grp, sData, grp[grp.dtype.names[0]][s_idx+1])
                else:
                    squad_var.main(pp, db, grpDb, sData, grp[grp.dtype.names[0]][s_idx+1])
            pp.close()
            
            # Merge the three pdfs
            file1 = PdfFileReader(line + '/qc_tables_tmp.pdf', 'rb')
            file2 = PdfFileReader(line + '/qc.pdf', 'rb')
            file3 = PdfFileReader(line + '/qc_tmp.pdf', 'rb')

            output = PdfFileWriter()

            output.addPage(file1.getPage(0))
            for i in np.arange(1,file2.numPages):
                output.addPage(file2.getPage(i))
            for i in np.arange(0,file3.numPages):
                output.addPage(file3.getPage(i))

            outputStream = open(line + '/qc_updated.pdf', 'wb')
            output.write(outputStream)
            outputStream.close()
            
            # Clear temporary pdf files
            os.remove(line + '/qc_tables_tmp.pdf')
            os.remove(line + '/qc_tmp.pdf')

            s_idx = s_idx + 1
            