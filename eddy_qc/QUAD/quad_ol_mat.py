#!/usr/bin/env fslpython

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn
seaborn.set()






#=========================================================================================
# QUAD - Outliers stats
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy):
    """
    Generate page of the single subject report pdf that contains:
    - bar plots of the number of outliers per PE directions and b-shell 
    - Z-stat matrix used to identify outliers and %outliers plot per volume
    
    Arguments:
        - pdf: qc pdf file
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
    """
    #================================================
    # Prepare figure
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle('Subject ' + data['subj_id'], fontsize=10, fontweight='bold')

    # Divide the page in two sections. Top one will have the bar plots, bottom (and bigger)
    # one will have the Z-stat matrix and %ol-per-volume plot sharing the matrix x axis.
    gs0 = gridspec.GridSpec(2, 1, height_ratios=[0.16, 0.8], hspace=0.2)

    # Top part: 2 bar plots
    gs00 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs0[0], wspace=0.5)

    ax1_00 = plt.subplot(gs00[0, 0])
    seaborn.barplot(x=np.arange(1, 1+data['no_PE_dirs']), y=eddy['pe_ol'], ax=ax1_00)
    ax1_00.set_xlabel("Phase encoding direction")
    ax1_00.set_ylabel("% outliers")
    ax1_00.set_xticklabels([np.array_str(data['eddy_para'][4*i:4*i+3]) for i in range(0, data['unique_pedirs'].size) ])

    ax2_00 = plt.subplot(gs00[0, 1]);
    seaborn.barplot(x=np.arange(1, 1+data['unique_bvals'].size), y=eddy['b_ol'], ax=ax2_00)
    ax2_00.set_xlabel("b-value [s/mm$^2$]")
    ax2_00.set_ylabel("% outliers")
    ax2_00.set_xticklabels([np.array_str(data['unique_bvals'][i]) for i in range(0, data['unique_bvals'].size) ])

    # Bottom part: Z-stat matrix and %outlier plot with shared x axis
    gs01 = gridspec.GridSpecFromSubplotSpec(3, 2, subplot_spec=gs0[1], width_ratios=[1, 0.05], height_ratios=[0.1, 0.8, 0.05], hspace=0.0)
    ax3_01 = plt.subplot(gs01[1, 0])
    ax4_01 = plt.subplot(gs01[1, 1])
    ax1_01 = plt.subplot(gs01[0, 0], sharex=ax3_01)
    
    ax1_01.plot(0.5+np.arange(0, data['bvals'].size), 100*np.sum(eddy['olMap'], axis=1)/eddy['olMap'].shape[1])
    ax1_01.set_ylabel("% outliers")
    ax1_01.set_ylim([0, 2+np.max(100*np.sum(eddy['olMap'], axis=1)/eddy['olMap'].shape[1])])
    ax1_01.yaxis.set_ticks([np.round(2+np.max(100*np.sum(eddy['olMap'], axis=1)/eddy['olMap'].shape[1]))/2, np.round(2+np.max(100*np.sum(eddy['olMap'], axis=1)/eddy['olMap'].shape[1]))])
    plt.setp(ax1_01.get_xticklabels(), visible=False)
    
    seaborn.heatmap(np.transpose(eddy['olMap_std']), ax=ax3_01, cbar_ax=ax4_01, cbar_kws={"orientation": "vertical", "label": "No. std. devs away from mean slice-difference"}, vmin=-4, vmax=4, xticklabels=int(data['bvals'].size/10), yticklabels=10, cmap='RdBu_r')
    ax3_01.set_xlabel("Volume")
    ax3_01.set_ylabel("Slice")
    
    # Format figure, save and close it
    plt.savefig(pdf, format='pdf')
    plt.close()
