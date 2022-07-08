import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set()







#=========================================================================================
# QUAD - Summary tables
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy, upd):
    """
    Generate page of the single subject report pdf that contains summary tables about the 
    data and qc indices.
    If group data is available, then put the single subject data in context.

    Arguments:
        - pdf: qc pdf file
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
        - upd: update flag
    """
    #================================================
    # Prepare figure
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle('Subject ' + data['subj_id'], fontsize=10, fontweight='bold')

    # Check eddy options to determine number of tables
    n_opts = 0
    if eddy['motionFlag']:
        n_opts = n_opts + 1
    if eddy['paramsFlag']:
        n_opts = n_opts + 1
    if eddy['fieldFlag']:
        n_opts = n_opts + 1
    if eddy['olFlag']:
        n_opts = n_opts + 1
    if eddy['cnrFlag']:
        n_opts = n_opts + 1

    # EDDY QC OUTPUT
    # Between volume motion
    idxLine = 0
    if eddy['s2vFlag']: 
        ax1 = plt.subplot2grid((n_opts,2), (idxLine,0), colspan=1)
    else:
        ax1 = plt.subplot2grid((n_opts,1), (idxLine,0), colspan=1)
    cell_text = [['Average abs. motion (mm)', '%1.2f' % eddy['avg_abs_mot'] ],
                 ['Average rel. motion (mm)', '%1.2f' % eddy['avg_rel_mot'] ],
                 ['Average x translation (mm)', '%1.2f' % eddy['avg_params'][0] ],
                 ['Average y translation (mm)', '%1.2f' % eddy['avg_params'][1] ],
                 ['Average z translation (mm)', '%1.2f' % eddy['avg_params'][2] ],
                 ['Average x rotation (deg)', '%1.2f' % np.rad2deg(eddy['avg_params'][3]) ],
                 ['Average y rotation (deg)', '%1.2f' % np.rad2deg(eddy['avg_params'][4]) ],
                 ['Average z rotation (deg)', '%1.2f' % np.rad2deg(eddy['avg_params'][5]) ],]
    ax1.axis('off')
    ax1.axis('tight')
    ax1.set_title('Volume-to-volume motion', fontsize=12, fontweight='bold',loc='left')
    if upd:
        tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', colWidths=[0.8, 0.2], rowLabels=[" . " for x in np.arange(0, 8)], rowColours=np.concatenate((eddy['mot_colour'], eddy['params_colour'][0:6])))
    else:
        tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', colWidths=[0.8, 0.2])
    tb.auto_set_font_size(False)
    tb.set_fontsize(9)
    tb.scale(1,1.5)

    # Within volume motion
    if eddy['s2vFlag']: 
        ax1 = plt.subplot2grid((n_opts,2), (idxLine,1), colspan=1)
        cell_text = [['Avg std x translation (mm)', '%1.2f' % eddy['avg_std_s2v_params'][0] ],
                    ['Avg std y translation (mm)', '%1.2f' % eddy['avg_std_s2v_params'][1] ],
                    ['Avg std z translation (mm)', '%1.2f' % eddy['avg_std_s2v_params'][2] ],
                    ['Avg std x rotation (deg)', '%1.2f' % eddy['avg_std_s2v_params'][3] ],
                    ['Avg std y rotation (deg)', '%1.2f' % eddy['avg_std_s2v_params'][4] ],
                    ['Avg std z rotation (deg)', '%1.2f' % eddy['avg_std_s2v_params'][5] ],]
        ax1.axis('off')
        ax1.axis('tight')
        ax1.set_title('Within-volume motion', fontsize=12, fontweight='bold',loc='left')
        if upd:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', colWidths=[0.8, 0.2], rowLabels=[" . " for x in np.arange(0, 6)],  rowColours=eddy['s2v_params_colour'])
        else:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', colWidths=[0.8, 0.2])
        tb.auto_set_font_size(False)
        tb.set_fontsize(9)
        tb.scale(1,1.5)
    
    # Outliers
    if eddy['olFlag']:
        idxLine = idxLine + 1
        cell_text = [['Total outliers (%)', '%1.2f' % eddy['tot_ol'] ],]
        for i in range(0, data['unique_bvals'].size):
            cell_text.append(['Outliers (b=%1.0f s/mm$^2$)' % data['unique_bvals'][i], '%1.2f' % eddy['b_ol'][i] ])
        for i in range(0, data['unique_pedirs'].size):
            cell_text.append(['Outliers (PE dir=' + np.array_str(data['eddy_para'][4*i:4*i+3]) + ')', '%1.2f' % eddy['pe_ol'][i] ])
        ax1 = plt.subplot2grid((n_opts,1), (idxLine,0), colspan=1)
        ax1.axis('off')
        ax1.axis('tight')
        ax1.set_title('Outliers', fontsize=12, fontweight='bold',loc='left')
        if upd:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', rowLabels=[" . " for x in np.arange(0, eddy['ol_colour'].shape[0])],  rowColours=eddy['ol_colour'])
        else:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left')
        tb.auto_set_font_size(False)
        tb.set_fontsize(9)
        tb.scale(1,1.5)
    
    # SNR/CNR
    if eddy['cnrFlag']:
        idxLine = idxLine + 1
        cell_text = [['Average SNR (b=0 s/mm$^2$)', '%1.2f' % eddy['avg_cnr'][0] ],]
        for i in range(0, data['unique_bvals'].size):
            cell_text.append(['Average CNR (b=%1.0f s/mm$^2$)' % data['unique_bvals'][i], '%1.2f' % eddy['avg_cnr'][i+1] ])
        ax1 = plt.subplot2grid((n_opts,1), (idxLine,0), colspan=1)
        ax1.axis('off')
        ax1.axis('tight')
        ax1.set_title('SNR/CNR', fontsize=12, fontweight='bold',loc='left')
        if upd:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', rowLabels=[" . " for x in np.arange(0, eddy['cnr_colour'].shape[0])],  rowColours=eddy['cnr_colour'])
        else:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left')
        tb.auto_set_font_size(False)
        tb.set_fontsize(9)
        tb.scale(1,1.5)
    
    # EC
    if eddy['paramsFlag']:
        idxLine = idxLine + 1
        cell_text = [['Std Dev EC linear term (x)', '%1.2f' % eddy['avg_params'][6] ],
                     ['Std Dev EC linear term (y)', '%1.2f' % eddy['avg_params'][7] ],
                     ['Std Dev EC linear term (z)', '%1.2f' % eddy['avg_params'][8] ],]
        ax1 = plt.subplot2grid((n_opts,1), (idxLine,0), colspan=1)
        ax1.axis('off')
        ax1.axis('tight')
        ax1.set_title('Eddy currents', fontsize=12, fontweight='bold',loc='left')
        if upd:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', rowLabels=[" . " for x in np.arange(0, 3)],  rowColours=eddy['params_colour'][6:9])
        else:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left')
        tb.auto_set_font_size(False)
        tb.set_fontsize(9)
        tb.scale(1,1.5)
    
    # Susceptibility
    if eddy['fieldFlag']:
        idxLine = idxLine + 1
        cell_text = [['Std Dev voxel displacement', '%1.2f' % eddy['std_displacement'] ],]
        ax1 = plt.subplot2grid((n_opts,1), (idxLine,0), colspan=1)
        ax1.axis('off')
        ax1.axis('tight')
        ax1.set_title('Susceptibility distortions', fontsize=12, fontweight='bold',loc='left')
        if upd:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left', rowLabels=[" . " for x in np.arange(0, eddy['field_colour'].shape[0])],  rowColours=eddy['field_colour'])
        else:
            tb = ax1.table(cellText=cell_text,loc='upper center',cellLoc='left')
        tb.auto_set_font_size(False)
        tb.set_fontsize(9)
        tb.scale(1,1.5)
    
    """
    # DATA SUMMARY
    idxLine = idxLine + 1
    cell_text = [['Volume size (x, y, z)', str(data['vol_size'][0]) + ', ' + str(data['vol_size'][1]) + ', ' + str(data['vol_size'][2])],
                 ['Voxel size (mm)', str(round(data['vox_size'][0],2)) + ', ' + str(round(data['vox_size'][1],2)) + ', ' + str(round(data['vox_size'][2],2))],
                 ['Acquired volumes','%1.0f' % (data['no_dw_vols']+data['no_b0_vols'])],
                 ['Acquired b0s',data['no_b0_vols']],
                 ['b-shells (s/mm$^2$)', ', '.join(map(str, data['unique_bvals']))],
                 ['Volumes per b-shell', ', '.join(map(str, data['bvals_dirs']))],
                 ['Number of PE directions',data['no_PE_dirs']],
                 ['Volumes per PE direction', ', '.join(map(str, data['pedirs_count']))]]
    ax2 = plt.subplot2grid((n_opts+1,1), (idxLine,0), colspan=1)
    ax2.axis('off')
    ax2.set_title('Data summary', fontsize=14, fontweight='bold',loc='left')
    tb = ax2.table(cellText=cell_text,loc='upper center',cellLoc='left')
    tb.auto_set_font_size(False)
    tb.set_fontsize(12)
    tb.scale(1,1.5)
    """

    # Format figure, save and close it
    plt.tight_layout(h_pad=1.5, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()
