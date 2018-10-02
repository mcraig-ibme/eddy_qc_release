#!/usr/bin/env fslpython

import glob
import os
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from eddy_qc.utils import fslpy
import seaborn
seaborn.set()


#=========================================================================================
# QUAD - Contrast to noise ratio (CNR) maps
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy):
    """
    Generate page of the single subject report pdf that contains 3 example slices (1 axial, 
    1 coronal and 1 sagittal) from each CNR map. There is a total of 1+N CNR maps, where N 
    is the number of acquired shells.
    
    Arguments:
        - pdf: qc pdf file
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
    """
    #================================================
    # Prepare figure
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle('Subject ' + data['subj_id'],fontsize=10, fontweight='bold')

    # Initialise counter and split the 4D file into single 3D CNR volumes
    count = 0
    fslpy.fslsplit(eddy['cnrFile'], data['qc_path'] + '/cnr')
    
    # Loop through the files, get orthogonal projections into PNGs and adjust colorbar
    for item in sorted(glob.glob(data['qc_path'] + '/cnr*.nii.gz')):
        vol = nib.load(item)
        vol = vol.get_data()
        vol[np.isnan(vol)] = 0
        # Maximum intensity definition
        i_max = np.round(np.mean(vol[:,:,:][data['mask'] != 0.0])+3*np.std(vol[:,:,:][data['mask'] != 0.0]),2)
        fslpy.slicer(item, a=item + ".png", i=(0, i_max))
        img=mpimg.imread(item + ".png")
        ax = plt.subplot2grid((1+data['unique_bvals'].size, 1), (count, 0))
        im = ax.imshow(img, interpolation='none', cmap="gray", vmin = 0, vmax=i_max)
        plt.colorbar(im, ax = ax)
        ax.grid(False)
        ax.axis('off')
        if count==0:
            ax.set_title('tSNR map (b=0)')
        else:
            ax.set_title('CNR map (b=%d)' % data['unique_bvals'][count-1])
        count+=1
    
    # Clear temporary volume files
    for f in glob.glob(data['qc_path'] + "/*.nii.gz"):
        os.remove(f)

    # Format figure, save and close it   
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()
