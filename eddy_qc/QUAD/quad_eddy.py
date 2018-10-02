#!/usr/bin/env fslpython

import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set()







#=========================================================================================
# QUAD - Eddy current linear parameters
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy):
    """
    Generate page of the single subject report pdf that contains plots of the estimated 
    eddy currents linear parameters for the three axes.
    
    Arguments:
        - pdf: qc pdf file
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
    """
    #================================================
    # Prepare figure
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle('Subject ' + data['subj_id'],fontsize=10, fontweight='bold')

    # Plot estimated eddy currents linear terms along the x-axis
    ax1 = plt.subplot2grid((3,1), (0,0))
    ax1.plot(eddy['params'][:,6], 'b', linewidth=2, label="x")
    ax1.set_xbound(1, data['bvals'].size)
    ax1.set_xlabel("Volume")
    ax1.set_ylabel("Hz/mm")
    ax1.set_title("Eddy currents linear terms (x-axis)")
    
    # Plot estimated eddy currents linear terms along the y-axis
    ax2 = plt.subplot2grid((3,1), (1,0))
    ax2.plot(eddy['params'][:,7], 'b', linewidth=2, label="y")
    ax2.set_xbound(1, data['bvals'].size)
    ax2.set_xlabel("Volume")
    ax2.set_ylabel("Hz/mm")
    ax2.set_title("Eddy currents linear terms (y-axis)")
    
    # Plot estimated eddy currents linear terms along the z-axis
    ax3 = plt.subplot2grid((3,1), (2,0))
    ax3.plot(eddy['params'][:,8], 'b', linewidth=2, label="z")
    ax3.set_xbound(1, data['bvals'].size)
    ax3.set_xlabel("Volume")
    ax3.set_ylabel("Hz/mm")
    ax3.set_title("Eddy currents linear terms (z-axis)")
    
    # Format figure, save and close it
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()