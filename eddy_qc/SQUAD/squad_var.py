#!/usr/bin/env fslpython

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pylab import MaxNLocator
import seaborn
seaborn.set()






#=========================================================================================
# SQUAD - Main group report
# Matteo Bastiani
# 01-08-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, db, grp, s_data, s_grp):
    """
    If a grouping variable is used, generate pages of the group report pdf that contains:
    - violin plots for outlier distributions
    - violin plots for absolute and relative motion
    - violin plots for CNR and SNR
    
    Arguments:
        - pdf: qc pdf file
        - data: data array
    """

    # Set cat_flag to true if grouping variable is categorical rather than continous
    cat_flag = False
    if grp[grp.dtype.names[0]][0] == 0:
        cat_flag = True


    #================================================
    # Prepare figure
    #================================================
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle("QUAD: Group report", fontsize=10, fontweight='bold')

    # MOTION
    ax1 = plt.subplot2grid((3, 1), (0, 0), colspan=1)
    if cat_flag:
        seaborn.violinplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_motion'][:,0], palette='Set3', scale='width', width=0.5, linewidth=1, inner='point', ax=ax1)
    else:
        seaborn.regplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_motion'][:,0], ax=ax1)
    seaborn.despine(left=True, bottom=True, ax=ax1)
    ax1.set_ylabel("mm")
    ax1.set_ylim(bottom=0)
    ax1.set_xlabel(grp.dtype.names[0])
    ax1.set_title("Average absolute motion")
    
    ax2 = plt.subplot2grid((3, 1), (1, 0), colspan=1)
    if cat_flag:
        seaborn.violinplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_motion'][:,1], palette='Set3', scale='width', width=0.5, linewidth=1, inner='point', ax=ax2)
    else:
        seaborn.regplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_motion'][:,1], ax=ax2)
    seaborn.despine(left=True, bottom=True, ax=ax2)
    ax2.set_ylabel("mm")
    ax2.set_ylim(bottom=0)
    ax2.set_xlabel(grp.dtype.names[0])
    ax2.set_title("Average relative motion")
    
    # If updating single subject reports
    if s_data is not None:
        ax1.scatter(s_grp, s_data['qc_mot_abs'], s=100, marker='*', c='w', edgecolors='k', linewidths=1 )
        ax2.scatter(s_grp, s_data['qc_mot_rel'], s=100, marker='*', c='w', edgecolors='k', linewidths=1 )
    
    # OUTLIERS
    if db['ol_flag']:
        ax3 = plt.subplot2grid((3, 1), (2, 0), colspan=1)
        if cat_flag:
            seaborn.violinplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_outliers'][:,0], palette='Set3', scale='width', width=0.5, linewidth=1, inner='point', ax=ax3)
        else:
            seaborn.regplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_outliers'][:,0], ax=ax3)
        seaborn.despine(left=True, bottom=True, ax=ax3)
        ax3.set_ylabel("%")
        ax3.set_ylim(bottom=0)
        ax3.set_xlabel(grp.dtype.names[0])
        ax3.set_title("Total outliers")
        
        # If updating single subject reports
        if (s_data is not None and
            s_data['qc_ol_flag']):
            ax3.scatter(s_grp, s_data['qc_outliers_tot'], s=100, marker='*', c='w', edgecolors='k', linewidths=1 )
    
    #================================================
    # Format figure, save and close it
    #================================================
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()

    #================================================
    # 2nd page (if needed): SNR and CNR
    #================================================
    if db['cnr_flag']:
        plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
        plt.suptitle("QUAD: Group report", fontsize=10, fontweight='bold')

        # SNR
        ax1 = plt.subplot2grid((1+db['data_no_shells'], 1), (0, 0), colspan=1)
        if cat_flag:
            seaborn.violinplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_cnr'][:,0], palette='Set3', scale='width', width=0.5, linewidth=1, inner='point', ax=ax1)
        else:
            seaborn.regplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_cnr'][:,0], ax=ax1)
        seaborn.despine(left=True, bottom=True, ax=ax1)
        ax1.set_ylim(bottom=0)
        ax1.set_xlabel(grp.dtype.names[0])
        ax1.set_title("b0 SNR")
        if (s_data is not None and
            s_data['qc_cnr_flag']):
            ax1.scatter(s_grp, s_data['qc_cnr_avg'][0], s=100, marker='*', c='w', edgecolors='k', linewidths=1 )
            
        # CNR
        for i in range(0, db['data_no_shells']):
            ax2 = plt.subplot2grid((1+db['data_no_shells'], 1), (1+i, 0), colspan=1)
            if cat_flag:
                seaborn.violinplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_cnr'][:, 1+i], palette='Set3', scale='width', width=0.5, linewidth=1, inner='point', ax=ax2)
            else:
                seaborn.regplot(x=grp[grp.dtype.names[0]][1:], y=db['qc_cnr'][:, 1+i], ax=ax2)
            seaborn.despine(left=True, bottom=True, ax=ax2)
            ax2.set_ylim(0, 1.5*np.max(db['qc_cnr'][:,1:]))
            ax2.set_xlabel(grp.dtype.names[0])
            ax2.set_title("CNR b" + str(db['data_unique_bvals'][i]))
            if (s_data is not None and
                s_data['qc_cnr_flag']):
                ax2.scatter(s_grp, s_data['qc_cnr_avg'][i+1], s=100, marker='*', c='w', edgecolors='k', linewidths=1 )
            
        #================================================
        # Format figure, save and close it
        #================================================
        plt.tight_layout(h_pad=1, pad=4)
        plt.savefig(pdf, format='pdf')
        plt.close()
