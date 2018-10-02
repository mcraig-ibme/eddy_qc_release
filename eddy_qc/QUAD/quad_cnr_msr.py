#!/usr/bin/env fslpython

import numpy as np
from pylab import MaxNLocator
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn
seaborn.set()





#=========================================================================================
# QUAD - Contrast to noise ratio (CNR) and mean squared residuals (MSR)
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy):
    """
    Generate page of the single subject report pdf that contains:
    - Per-shell average CNR bar plots (error bars are standard deviations).
    - Per-volume mean squared residuals plots (one plot for each b-value, including 0). Outliers
    (MSR > mean + std for each shell) are marked as red stars with the number of corresponding volume
    (0-based) next to them.
    
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
    # one will have the MSR plots.
    gs0 = gridspec.GridSpec(2, 1, height_ratios=[0.16, 0.8], hspace=0.2)

    gs00 = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs0[0], wspace=1)
    ax1_00 = plt.subplot(gs00[0, 0])
    sb = seaborn.barplot(y=eddy['avg_cnr'][0], ax=ax1_00)
    sb.errorbar(x=0, y=eddy['avg_cnr'][0], yerr=eddy['std_cnr'][0], ecolor='black', fmt="none")
    ax1_00.set_xlabel("b-value [s/mm$^2$]")
    ax1_00.set_ylabel("tSNR")
    ax1_00.set_ylim(0, eddy['avg_cnr'][0]+2*eddy['std_cnr'][0])
    ax1_00.set_xticklabels([0])

    ax2_00 = plt.subplot(gs00[0, 1:]);
    sb = seaborn.barplot(x=np.arange(1, 1+data['unique_bvals'].size), y=eddy['avg_cnr'][1:], ci=3.0, ax=ax2_00)
    sb.errorbar(x=np.arange(0, data['unique_bvals'].size), y=eddy['avg_cnr'][1:], yerr=eddy['std_cnr'][1:], ecolor='black', fmt="none")
    ax2_00.set_xlabel("b-value [s/mm$^2$]")
    ax2_00.set_ylabel("CNR")
    ax2_00.set_xticklabels([np.array_str(data['unique_bvals'][i]) for i in range(0, data['unique_bvals'].size) ])
    
    if eddy['rssFlag']:
        gs01 = gridspec.GridSpecFromSubplotSpec(1+data['unique_bvals'].size, 1, subplot_spec=gs0[1])
        x = np.arange(data['bvals'].size)
        ax = plt.subplot(gs01[0, 0])
        tmp_rss = eddy['avg_rss'][np.abs(data['bvals']) <= 100]
        x_rss = x[np.abs(data['bvals']) <= 100]
        idxs = np.array(np.where(tmp_rss > np.mean(tmp_rss) + 2*np.std(tmp_rss)))
        ax.plot(np.arange(1, 1+data['no_b0_vols']), tmp_rss, label="b=0")
        ax.scatter(idxs+1, np.ones(idxs.size)*np.max(tmp_rss)+200, s=50, c='r', marker='*', label='Outliers')
        ol_vols = x_rss[idxs]
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title("Mean squared residuals (MSR)")
        ax.set_xlim(0, 1+data['no_b0_vols'])
        ax.set_ylabel("MSR")
        ax.legend(loc='best', frameon=True, framealpha=0.5)
        for i in range(0, data['unique_bvals'].size):
            tmp_rss = eddy['avg_rss'][np.abs(data['bvals']-data['unique_bvals'][i]) <= 100]
            x_rss = x[np.abs(data['bvals']-data['unique_bvals'][i]) <= 100]
            idxs = np.array(np.where(tmp_rss > np.mean(tmp_rss) + 2*np.std(tmp_rss)))
            ax = plt.subplot(gs01[i+1, 0])
            ax.set_ylabel("MSR")
            ax.plot(np.arange(1, 1+data['bvals_dirs'][i]), tmp_rss, label="b=%d" % data['unique_bvals'][i])
            ax.scatter(idxs+1, np.ones(idxs.size)*np.max(tmp_rss)+0.5*np.max(tmp_rss), s=50, c='r', marker='*', label='Outliers')
            ol_vols = np.append(ol_vols, x_rss[idxs])
            ax.xaxis.set_major_locator(MaxNLocator(integer=True))
            ax.set_xlim(0, 1+data['bvals_dirs'][i])
            ax.legend(loc='best', frameon=True, framealpha=0.5)
        ax.set_xlabel("Volume")

        # Save volumes without outliers to text files.
        # If bvecs have been specified, then also save reduced bvals and bvecs
        vols_no_outliers = np.delete(x, ol_vols)
        np.savetxt(data['qc_path'] + '/vols_no_outliers.txt', np.reshape(vols_no_outliers, (1,-1)), fmt='%d', delimiter=' ')
        if data['bvecs'].size != 0:
            np.savetxt(data['qc_path'] + '/bvecs_no_outliers.txt', data['bvecs'][:, vols_no_outliers], fmt='%.5f', delimiter=' ')
            np.savetxt(data['qc_path'] + '/bvals_no_outliers.txt', np.reshape(data['bvals'][vols_no_outliers], (1,-1)), fmt='%f', delimiter=' ')
        
    # Format figure, save and close it
    plt.savefig(pdf, format='pdf')
    plt.close()
