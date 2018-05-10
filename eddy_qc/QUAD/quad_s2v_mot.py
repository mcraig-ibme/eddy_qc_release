#!/usr/bin/env fslpython

import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set()







#=========================================================================================
# QUAD - Motion parameters
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy):
    """
    Generate page of the single subject report pdf that contains plots of the estimated 
    within volume motion parameters.
    Absolute and relative displacement plots are also shown.
    
    Arguments:
        - pdf: qc pdf file
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
    """
    #================================================
    # Prepare figure
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle('Subject ' + data['subj_id'],fontsize=10, fontweight='bold')

    # Plot std of estimated within volume translations along the 3 axes
    ax1 = plt.subplot2grid((2,1), (0,0))
    ax1.plot(np.sqrt(eddy['var_s2v_params'][:,0]), 'r', linewidth=2, label="x")
    ax1.plot(np.sqrt(eddy['var_s2v_params'][:,1]), 'g', linewidth=2, label="y")
    ax1.plot(np.sqrt(eddy['var_s2v_params'][:,2]), 'b', linewidth=2, label="z")
    ax1.set_xbound(1, data['bvals'].size)
    ax1.set_xlabel("Volume")
    ax1.set_ylabel("Std translation [mm]")
    ax1.set_title("Eddy estimated within volume translations (mm)")
    ax1.legend(loc='best', frameon=True, framealpha=0.5)
    ax1.set_ylim(bottom = 0)

    # Plot std of estimated within volume rotations around the 3 axes
    ax2 = plt.subplot2grid((2,1), (1,0))
    ax2.plot(np.sqrt(eddy['var_s2v_params'][:,3]), 'r', linewidth=2, label="x")
    ax2.plot(np.sqrt(eddy['var_s2v_params'][:,4]), 'g', linewidth=2, label="y")
    ax2.plot(np.sqrt(eddy['var_s2v_params'][:,5]), 'b', linewidth=2, label="z")
    ax2.set_xbound(1, data['bvals'].size)
    ax2.set_xlabel("Volume")
    ax2.set_ylabel("Std rotation [deg]")
    ax2.set_title("Eddy estimated within volume rotations (deg)")
    ax2.legend(loc='best', frameon=True, framealpha=0.5)
    ax2.set_ylim(bottom = 0)

    # Format figure, save and close it
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()