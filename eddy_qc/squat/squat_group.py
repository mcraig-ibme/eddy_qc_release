#!/usr/bin/env fslpython
"""
squat - Main group report

Matteo Bastiani, FMRIB, Oxford
Martin Craig, SPMIC, Nottingham
"""
import numpy as np
import matplotlib.pyplot as plt
from pylab import MaxNLocator
import seaborn
seaborn.set()

def main(pdf, db, grp, s_data):
    """
    Generate page of the group report pdf that contains:
    - bar plots of the number of acquired volumes for each subject
    - violin plots for outlier distributions
    - violin plots for absolute and relative motion
    - violin plots for CNR and SNR
    
    Arguments:
        - pdf: qc pdf file
        - db: dictionary database
        - grp: optional grouping variable
        - s_data: single subject dictionary to update pdf
    """
    #================================================
    # Prepare figure
    #================================================
    plt.figure(figsize=(8.27, 11.69))   # Standard portrait A4 sizes
    plt.suptitle("SQUAT: Group report", fontsize=10, fontweight='bold')

    ## Groups
    if grp is not False:
        ax1_00 = plt.subplot2grid((3, 4), (0, 0), colspan=1)
        g = seaborn.distplot(grp[grp.dtype.names[0]][1:], vertical=True, bins=np.arange(-1.5+round(min(grp[grp.dtype.names[0]][1:])),1.5+round(max(grp[grp.dtype.names[0]][1:]))), norm_hist=False, kde=False, ax=ax1_00)
        ax1_00.set_ylabel(grp.dtype.names[0])
        ax1_00.set_xlabel("N")
        # ax1_00.set_xlim([-1+round(min(grp[grp.dtype.names[0]][1:])),1+round(max(grp[grp.dtype.names[0]][1:]))])
        # ax1_00.set_xticks(np.unique(np.round(grp[grp.dtype.names[0]])))
        ax1_00.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax1_00.set_xticks([0, np.max(ax1_00.get_xticks())])

    ## Bar plot of number of acquired volumes per subject
    if "data_protocol" in db:
        ax1_01 = plt.subplot2grid((3, 4), (0, 0), colspan=4 if grp is False else 3)
        seaborn.barplot(x=np.arange(1, 1+db['data_num_subjects']),
                        y=np.sum(db['data_protocol'], axis=1),
                        color='blue', ax=ax1_01)
        n_vols, counts = np.unique(np.sum(db['data_protocol'], axis=1), return_counts=True)
        n_vols_mode = n_vols[np.argmax(counts)]
        n_vols_ol = 1 + np.where(np.sum(db['data_protocol'], axis=1) != n_vols_mode )[0] 
        ax1_01.set_xticks(n_vols_ol)
        ax1_01.set_xticklabels(n_vols_ol)
        ax1_01.tick_params(labelsize=6)
        plt.setp(ax1_01.get_xticklabels(), rotation=90)
        ax1_01.set_ylim(bottom=0)
        ax1_01.set_xlabel("Subject")
        ax1_01.set_ylabel("No. acquired volumes")
    
    ## Motion
    if "qc_motion" in db:
        # Absolute
        ax2_00 = plt.subplot2grid((3, 4), (1, 0), colspan=1)
        seaborn.violinplot(data=db['qc_motion'][:,0], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_00)
        seaborn.despine(left=True, bottom=True, ax=ax2_00)
        ax2_00.set_ylabel("mm (avg)")
        ax2_00.set_ylim(bottom=0)
        ax2_00.set_title("Abs. motion")
        ax2_00.set_xticklabels([""])
        # Relative
        ax2_01 = plt.subplot2grid((3, 4), (1, 1), colspan=1)
        seaborn.violinplot(data=db['qc_motion'][:,1], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_01)
        seaborn.despine(left=True, bottom=True, ax=ax2_01)
        ax2_01.set_ylabel("mm (avg)")
        ax2_01.set_ylim(bottom=0)
        ax2_01.set_title("Rel. motion")
        ax2_01.set_xticklabels([""])

        # Add subject marker if this is a single-subject version of the report
        if s_data is not None:
            ax2_00.scatter(0, s_data['qc_mot_abs'], s=100, marker='*', c='w', edgecolors='k', linewidths=1 )
            ax2_01.scatter(0, s_data['qc_mot_rel'], s=100, marker='*', c='w', edgecolors='k', linewidths=1 )
    
    # EDDY PARAMETERS
    if db['par_flag']:
        # Translations
        ax2_02 = plt.subplot2grid((3, 4), (1, 2), colspan=1)
        seaborn.violinplot(data=db['qc_parameters'][:,0:3], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_02)
        seaborn.despine(left=True, bottom=True, ax=ax2_02)
        ax2_02.set_ylabel("mm (avg)")
        ax2_02.set_title("Translations")
        ax2_02.set_xticklabels(["x", "y", "z"])
        # Rotations
        ax2_03 = plt.subplot2grid((3, 4), (1, 3), colspan=1)
        seaborn.violinplot(data=np.rad2deg(db['qc_parameters'][:,3:6]), scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_03)
        seaborn.despine(left=True, bottom=True, ax=ax2_03)
        ax2_03.set_ylabel("deg (avg)")
        ax2_03.set_title("Rotations")
        ax2_03.set_xticklabels(["x", "y", "z"])

        # Eddy currents
        ec_span = 4
        vd_span = 0
        if db['susc_flag']:
            ec_span = ec_span - 1
            vd_span = 1
        if db['s2v_par_flag']:
            ec_span = ec_span - 2
        ax3_00 = plt.subplot2grid((3, 4), (2, 0), colspan=ec_span)
        seaborn.violinplot(data=db['qc_parameters'][:,6:9], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax3_00)
        seaborn.despine(left=True, bottom=True, ax=ax3_00)
        ax3_00.set_title("EC linear terms")
        ax3_00.set_ylabel("Hz/mm (std)")
        ax3_00.set_xticklabels(["x", "y", "z"])
        ax3_00.set_ylim(bottom=0)
        # Check if needs to update single subject reports
        if s_data is not None:
            ax2_02.scatter([0, 1, 2], s_data['qc_params_avg'][0:3], s=100, marker='*', c='w', edgecolors='k', linewidths=1)
            ax2_03.scatter([0, 1, 2], np.rad2deg(s_data['qc_params_avg'][3:6]), s=100, marker='*', c='w', edgecolors='k', linewidths=1)
            ax3_00.scatter([0, 1, 2], s_data['qc_params_avg'][6:9], s=100, marker='*', c='w', edgecolors='k', linewidths=1)

        # Susceptibility
        if db['susc_flag']:
            ax3_00 = plt.subplot2grid((3, 4), (2, ec_span), colspan=vd_span)
            seaborn.violinplot(data=db['qc_susceptibility'], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax3_00)
            seaborn.despine(left=True, bottom=True, ax=ax3_00)
            ax3_00.set_title("Susceptibility")
            ax3_00.set_ylabel("Vox (std)")
            ax3_00.set_xticklabels([""])
            ax3_00.set_ylim(bottom=0)
            if s_data is not None:
                ax3_00.scatter(0, s_data['qc_vox_displ_std'], s=100, marker='*', c='w', edgecolors='k', linewidths=1)

        # S2V motion
        if db['s2v_par_flag']:
            # Translations
            ax3_00 = plt.subplot2grid((3, 4), (2, ec_span+vd_span), colspan=1)
            seaborn.violinplot(data=db['qc_s2v_parameters'][:,0:3], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax3_00)
            seaborn.despine(left=True, bottom=True, ax=ax3_00)
            ax3_00.set_title("S2V translations")
            ax3_00.set_ylabel("mm (std)")
            ax3_00.set_xticklabels(["x", "y", "z"])
            ax3_00.set_ylim(bottom=0)
            if s_data is not None:
                ax3_00.scatter([0, 1, 2], s_data['qc_s2v_params_avg_std'][0:3], s=100, marker='*', c='w', edgecolors='k', linewidths=1)
            # Rotations
            ax3_00 = plt.subplot2grid((3, 4), (2, ec_span+vd_span+1), colspan=1)
            seaborn.violinplot(data=db['qc_s2v_parameters'][:,3:6], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax3_00)
            seaborn.despine(left=True, bottom=True, ax=ax3_00)
            ax3_00.set_title("S2V rotations")
            ax3_00.set_ylabel("deg (std)")
            ax3_00.set_xticklabels(["x", "y", "z"])
            ax3_00.set_ylim(bottom=0)
            if s_data is not None:
                ax3_00.scatter([0, 1, 2], s_data['qc_s2v_params_avg_std'][3:6], s=100, marker='*', c='w', edgecolors='k', linewidths=1)

    #================================================
    # Format figure, save and close it
    #================================================
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()
        
    # OUTLIERS AND CNR
    if db['ol_flag'] or db['cnr_flag']:
        plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
        plt.suptitle("SQUAT: Group report", fontsize=10, fontweight='bold')
        
        # Look for shared b-values and PE directions if updating single subject reports
        if s_data is not None:
            b_db = (np.array(db['data_unique_bvals'])).reshape(-1,1)
            b_sub = (np.array(s_data['data_unique_bvals'])).reshape(-1,1)
            common_b = np.array(np.all((np.abs(b_db[:,None,:]-b_sub[None,:,:])<100),axis=-1).nonzero()).T
            pe_db = np.reshape(np.atleast_2d(db['data_unique_pes']), (-1,4))[:,0:3]
            pe_sub = np.reshape(np.atleast_2d(s_data['data_eddy_para']), (-1,4))[:,0:3]
            common_pe = np.array(np.all((pe_db[:,None,:]==pe_sub[None,:,:]),axis=-1).nonzero()).T        

        # OUTLIERS
        if db['ol_flag']:
            # Total
            ax1_00 = plt.subplot2grid((2, 3), (0, 0), colspan=1)
            seaborn.violinplot(data=db['qc_outliers'][:,0], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax1_00)
            seaborn.despine(left=True, bottom=True, ax=ax1_00)
            ax1_00.set_title("Total outliers")
            ax1_00.set_ylabel("%")
            ax1_00.set_ylim(bottom=0)
            ax1_00.set_xticklabels([""])
            # b-shell
            ax1_01 = plt.subplot2grid((2, 3), (0, 1), colspan=1)
            seaborn.violinplot(data=db['qc_outliers'][:,1:1+db['data_no_shells']], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax1_01)
            seaborn.despine(left=True, bottom=True, ax=ax1_01)
            ax1_01.set_ylabel("%")
            ax1_01.set_ylim(bottom=0)
            ax1_01.set_title("b-value outliers")
            ax1_01.set_xticklabels(db['data_unique_bvals'])
            ax1_01.set_xlabel("b-value")
            # PE direction
            ax1_02 = plt.subplot2grid((2, 3), (0, 2), colspan=1)
            seaborn.violinplot(data=db['qc_outliers'][:,1+db['data_no_shells']:], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax1_02)
            seaborn.despine(left=True, bottom=True, ax=ax1_02)
            ax1_02.set_title("PE dir. outliers")
            ax1_02.set_ylabel("%")
            ax1_02.set_ylim(bottom=0)
            ax1_02.set_xlabel("PE direction")
            # Check if needs to update single subject reports
            if (s_data is not None and
                s_data['qc_ol_flag']):
                ax1_00.scatter(0, s_data['qc_outliers_tot'], s=100, marker='*', c='w', edgecolors='k', linewidths=1)
                ax1_01.scatter(common_b[:,0], np.array(s_data['qc_outliers_b'])[common_b[:,1]], s=100, marker='*', c='w', edgecolors='k', linewidths=1)
                ax1_02.scatter(common_pe[:,0], np.array(s_data['qc_outliers_pe'])[common_pe[:,1]], s=100, marker='*', c='w', edgecolors='k', linewidths=1)
                

        if db['cnr_flag']:
            vox_volume = np.prod(np.array(db['data_vox_size']))
            # SNR
            ax2_01 = plt.subplot2grid((2, 3), (1, 0), colspan=1)
            # seaborn.violinplot(data=np.sqrt(db['data_no_b0_vols'])*db['qc_cnr'][:,0]/np.sqrt(vox_volume), scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_01)

            seaborn.violinplot(data=db['qc_cnr'][:,0], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_01)
            seaborn.despine(left=True, bottom=True, ax=ax2_01)
            ax2_01.set_ylim(bottom = 0)
            ax2_01.set_title("SNR (avg)")
            ax2_01.set_xticklabels("0")
            ax2_01.set_xlabel("b-value")
            
            # CNR
            ax2_02 = plt.subplot2grid((2, 3), (1, 1), colspan=2)
            # seaborn.violinplot(data=np.sqrt(db['data_no_dw_vols']/db['data_no_shells'])*db['qc_cnr'][:,1:]/np.sqrt(vox_volume), scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_02)

            seaborn.violinplot(data=db['qc_cnr'][:,1:], scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax2_02)
            seaborn.despine(left=True, bottom=True, ax=ax2_02)
            ax2_02.set_ylim(bottom = 0)
            ax2_02.set_title("CNR (avg)")
            ax2_02.set_xlabel("b-value")
            ax2_02.set_xticklabels(db['data_unique_bvals'])
            # Check if needs to update single subject reports
            if (s_data is not None and
                s_data['qc_cnr_flag']):
                ax2_01.scatter(0, s_data['qc_cnr_avg'][0], s=100, marker='*', c='w', edgecolors='k', linewidths=1)
                ax2_02.scatter(common_b[:,0], np.array(s_data['qc_cnr_avg'][1:])[common_b[:,1]], s=100, marker='*', c='w', edgecolors='k', linewidths=1)
                
        #================================================
        # Format figure, save and close it
        #================================================
        plt.tight_layout(h_pad=1, pad=4)
        plt.savefig(pdf, format='pdf')
        plt.close()
