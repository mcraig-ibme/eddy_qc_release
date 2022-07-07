#!/usr/bin/env fslpython
"""
GSQUAD - Individual or group report

Matteo Bastiani, FMRIB, Oxford
Martin Craig, SPMIC, Nottingham
"""
import numpy as np
import matplotlib.pyplot as plt
from pylab import MaxNLocator
import seaborn
seaborn.set()

def save_page(pdf):
    print("Saving page")
    plt.tight_layout(h_pad=1, pad=4)
    plt.savefig(pdf, format='pdf')
    plt.close()

def new_page():
    print("Starting new page")
    plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
    plt.suptitle("SQUAD: Group report", fontsize=10, fontweight='bold')

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
    report = db.get("gsquad_report", {})
    rows_per_page = 3

    if False and grp is not False:
        # Plot of distribution of grouping variable
        # FIXME not functional, just capturing info from SQUAD code
        data = grp[grp.dtype.names[0]][1:]
        report.insert(0, [
            {
                "data" : data,
                "plottype" : "distplot",
                "bins" : np.arange(-1.5+round(min(data)),1.5+round(max(data))),
                "kde" : False,
                "norm_hist" : False,
                "vertical" : True,
                "ylabel" : grp.dtype.names[0],
                "xlabel" : "N",
            }
        ])
        
        # ax1_00.set_xlim([-1+round(min(grp[grp.dtype.names[0]][1:])),1+round(max(grp[grp.dtype.names[0]][1:]))])
        # ax1_00.set_xticks(np.unique(np.round(grp[grp.dtype.names[0]])))
        #ax1_00.xaxis.set_major_locator(MaxNLocator(integer=True))
        #ax1_00.set_xticks([0, np.max(ax1_00.get_xticks())])

    if False and "data_protocol" in db:
        # Bar plot of number of acquired volumes per subject
        # FIXME eddy specific and not functional, just capturing code from SQUAD
        report.insert(0, [
            {
                "plottype" : "barplot",
                "x" : np.arange(1, 1+db['data_num_subjects']),
                "y" : np.sum(db['data_protocol'], axis=1),
                "color" : "blue",
            }
        ])
        
        # n_vols, counts = np.unique(np.sum(db['data_protocol'], axis=1), return_counts=True)
        # n_vols_mode = n_vols[np.argmax(counts)]
        # n_vols_ol = 1 + np.where(np.sum(db['data_protocol'], axis=1) != n_vols_mode )[0] 
        # ax1_01.set_xticks(n_vols_ol)
        # ax1_01.set_xticklabels(n_vols_ol)
        # ax1_01.tick_params(labelsize=6)
        # plt.setp(ax1_01.get_xticklabels(), rotation=90)
        # ax1_01.set_ylim(bottom=0)
        # ax1_01.set_xlabel("Subject")
        # ax1_01.set_ylabel("No. acquired volumes")

    num_cols = max([len(plots) for plots in report])

    for group_idx, plots in enumerate(report):
        if group_idx % rows_per_page == 0:
            # Start new page
            if group_idx > 0:
                # Format and save previous page
                save_page(pdf)
            new_page()

        print(f"Plotting group {plots}")
        group_num_cols = sum([plot.get("colspan", 1) for plot in plots])
        current_col = 0

        for plot_idx, plot in enumerate(plots):
            data_item = plot.pop("var", None)
            if data_item is None:
                print(f"WARNING: Plot variable not defined {plot}")
                continue
            print(f"Plotting variable {data_item}")
            data_values = np.array(db['qc_' + data_item])

            # If there are fewer plots than columns, make initial plots span an extra column
            colspan = plot.pop("colspan", 1) 
            if group_num_cols < num_cols and plot_idx < (num_cols - group_num_cols):
                colspan += 1
                #print(f"Increasing colspan for {plot_var} to {colspan}")

            ax = plt.subplot2grid((rows_per_page, num_cols), (group_idx % rows_per_page, current_col), colspan=colspan)
            current_col += colspan

            #print(f"Data: {data_values}")
            seaborn.violinplot(data=data_values, scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax)
            seaborn.despine(left=True, bottom=True, ax=ax)
            for arg, value in plot.items():
                #print(f"Setting {arg}={value}")
                if arg in ["xticklabels",] and isinstance(value, str):
                    value = db[value]
                    #print(f"Setting {arg}={value}")
                setter = getattr(ax, f"set_{arg}", None)
                if setter is not None:
                    setter(value)

    # Save last page
    save_page(pdf)
