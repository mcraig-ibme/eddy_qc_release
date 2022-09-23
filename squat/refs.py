"""
SQUAT: Reference page generator

Matteo Bastiani, FMRIB, Oxford & SPMIC, Nottingham
Martin Craig: SPMIC, Nottingham
"""

import os
import tempfile

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.gridspec as gridspec
import seaborn

seaborn.set()

def main(pdf, refs_fname=None):
    """
    Generate page of the single subject report pdf that contains eddy-related references.
    
    Arguments:
        - pdf: qc pdf file
        - refs_fname: Filename containing references
    """
    if refs_fname:
        try:
            with open(refs_fname, "r") as f:
                refs_text = f.readlines()
        except IOError as exc:
            raise ValueError(f"Failed to read references file {refs_fname}: {exc}")
    else:
        refs_text = ""

    with tempfile.NamedTemporaryFile(suffix=".png") as img_file:
        # Prepare reference figure
        plt.figure(figsize=(8.27, 11.69))   # Standard portrait A4 sizes
        gs0 = gridspec.GridSpec(2, 1, height_ratios=[0.16, 0.8], hspace=0.2)

        # Top part: logos
        gs00 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=gs0[0])
        ax1_00 = plt.subplot(gs00[0, 0])
        resource_dir = os.path.dirname(__file__)
        logos = os.path.join(resource_dir, 'utils/eddy_qc_logos.png')
        img = mpimg.imread(logos)
        im = ax1_00.imshow(img, interpolation='none')
        ax1_00.axis('off')
        ax1_00.set_position([-0.07, 0.77878787878787881, 1.5*0.77500000000000002, 1.5*0.12121212121212122])

        # Bottom part: text + references
        gs01 = gridspec.GridSpecFromSubplotSpec(1, 1, subplot_spec=gs0[1])
        ax1_01 = plt.subplot(gs01[0, 0])
        plt.text(-0.15, 1, refs_text, size=11, wrap=True, transform=ax1_01.transAxes, va='top', ha='left')
        ax1_01.axis('off')
        
        # Format figure, save and close it
        plt.savefig(img_file.name, format='png', dpi=300)
        plt.close()

        # Save text file with references
        #with open(data['qc_path'] + '/ref.txt', 'w') as f:
        #    f.write(ec.MethodsText())

        # Regenerate new figure and load the previously stored one to avoid issues 
        # with text wrapping
        plt.figure(figsize=(8.27, 11.69))   # Standard portrait A4 sizes
        # plt.suptitle('Subject ' + data['subj_id'], fontsize=10, fontweight='bold')

        img = mpimg.imread(img_file.name)
        ax = plt.subplot2grid((1, 1), (0, 0))
        im = ax.imshow(img, interpolation='none')
        # plt.colorbar(im, ax=ax)
        # ax.axes.get_yaxis().set_ticks([])
        seaborn.despine()
        ax.grid(False)
        ax.axis('off')

        pos = ax.get_position()
        pos2 = [0.1075, pos.y0, pos.width, pos.height]
        ax.set_position(pos2)

        plt.savefig(pdf, format='pdf')
        plt.close()
