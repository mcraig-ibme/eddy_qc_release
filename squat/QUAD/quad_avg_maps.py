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
# QUAD - Average b-shell maps
# Matteo Bastiani
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def main(pdf, data, eddy):
    """
    Generate page of the single subject report pdf that contains 3 example slices (1 axial, 
    1 coronal and 1 sagittal) from each averaged DW map. There is a total of 1+N volumes, 
    where N is the number of acquired shells.
    
    Arguments:
        - pdf: qc pdf file
        - data: data dictionary containg information about the dataset
        - eddy: EDDY dictionary containg useful qc information
    """
    #================================================
    # Prepare figure
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle('Subject ' + data['subj_id'],fontsize=10, fontweight='bold')

    # Compute average b=0 volume
    # fslpy.select_dwi_vols(data=data['subj_id'], bvals=data['bvals_id'], output=data['qc_path'] + "/avg_b0", b=5, m=True)
    vol = nib.Nifti1Image(np.mean(data['eddy_epi'].get_data()[..., data['bvals']==0], axis=3), data['eddy_epi'].get_affine(), data['eddy_epi'].header)
    nib.save(vol, data['qc_path'] + "/avg_b0.nii.gz")
    vol = vol.get_data()
    # Maximum intensity definition
    i_max = np.round(np.mean(vol[:,:,:][data['mask'] != 0.0])+3*np.std(vol[:,:,:][data['mask'] != 0.0]))
    fslpy.slicer(data['qc_path'] + "/avg_b0", a=data['qc_path'] + "/avg_b0.png", i=(0, i_max))
    img = mpimg.imread(data['qc_path'] + "/avg_b0.png")
    ax = plt.subplot2grid((1+data['unique_bvals'].size, 1), (0, 0))
    im = ax.imshow(img, interpolation='none', cmap="gray", vmin = 0, vmax=i_max)
    plt.colorbar(im, ax = ax)
    ax.grid(False)
    ax.axis('off')
    ax.set_title("Average DW signal (b=0)")
    data['eddy_epi'].uncache()
    del vol
    
    count = 1
    for b in data['unique_bvals']:
        # Compute average b=x volume
        # fslpy.select_dwi_vols(data=data['subj_id'], bvals=data['bvals_id'], output=data['qc_path'] + "/avg_b" + str(b), b=b, m=True)
        vol = nib.Nifti1Image(np.mean(data['eddy_epi'].get_data()[..., data['bvals']==b], axis=3), data['eddy_epi'].get_affine(), data['eddy_epi'].header)
        nib.save(vol, data['qc_path'] + "/avg_b" + str(b) + ".nii.gz")
        vol = vol.get_data()
        i_max = np.round(np.mean(vol[:,:,:][data['mask'] != 0.0])+3*np.std(vol[:,:,:][data['mask'] != 0.0]))
        fslpy.slicer(data['qc_path'] + "/avg_b" + str(b), a=data['qc_path'] + "/avg_b" + str(b) + ".png", i=(0, i_max))
        img=mpimg.imread(data['qc_path'] + "/avg_b" + str(b) + ".png")
        ax = plt.subplot2grid((1+data['unique_bvals'].size, 1), (count, 0))
        im = ax.imshow(img, interpolation='none', cmap="gray", vmin = 0, vmax=i_max)
        plt.colorbar(im, ax = ax)
        ax.grid(False)
        ax.axis('off')
        ax.set_title("Average DW signal (b=" + str(b) + ")")
        count+=1
        data['eddy_epi'].uncache()
        del vol
    
    # Clear temporary volume files
    for f in glob.glob(data['qc_path'] + "/*.nii.gz"):
        os.remove(f)

    # Format figure, save and close it
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()
    