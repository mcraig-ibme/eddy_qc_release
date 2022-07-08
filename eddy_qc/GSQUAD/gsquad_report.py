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

def main(pdf, db, s_data=None):
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

    table_rows = 4
    table_columns = 2
    # Colormap to mark outliers in the summary tables
    colours = np.array([[0.18, 0.79, 0.22, 0.5], [0.91, 0.71, 0.09, 0.5], [0.8, 0.20, 0.20, 0.5], [0, 0, 0, 0]])

    if s_data is not None:
        # For individual subject report, generate tables
        table_idx, table_title, table_content, table_colours = 0, None, [], []
        for group_idx, plots in enumerate(report):
            # Get the axes on which to create the table FIXME count how many distinct tables

            for plot_idx, plot in enumerate(plots):
                plot = dict(plot)
                new_table_title = plot.get("group_title", table_title)
                if new_table_title != table_title:
                    if table_title is not None:
                        if table_idx % (table_rows*table_columns) == 0:
                            if table_idx > 0:
                                save_page(pdf)
                            new_page()
                        # Starting a new table - display the previous one first
                        ax = plt.subplot2grid((table_rows, table_columns), (table_idx//table_columns, table_idx % table_columns))
                        ax.axis('off')
                        ax.axis('tight')
                        ax.set_title(table_title, fontsize=12, fontweight='bold',loc='left')
                        tb = ax.table(
                            cellText=table_content, 
                            cellColours=table_colours,
                            loc='upper center',
                            cellLoc='left',
                            colWidths=[0.8, 0.2],
                            #rowLabels=[" . "] * len(table_content),
                            #rowColours=np.concatenate((eddy['mot_colour'], eddy['params_colour'][0:6]))
                        )
                        tb.auto_set_font_size(False)
                        tb.set_fontsize(9)
                        tb.scale(1,1.5)
                        table_idx += 1
                        table_content = []
                        table_colours = []
                    table_title = new_table_title

                # Get the data variable and add all values to the table with appropriate label
                data_item = plot.pop("var", None)
                if data_item is None:
                    print(f"WARNING: Variable not defined {plot}")
                    continue
                data_values = np.atleast_1d(s_data['qc_' + data_item])
                group_values = db['qc_' + data_item]
                mean = np.atleast_1d(np.mean(group_values, axis=0) + 1e-10)
                std = np.atleast_1d(np.std(group_values, axis=0) + 1e-10)
                for idx, value in enumerate(data_values):
                    row_label = plot.get("title", "")
                    if "xticklabels" in plot:
                        xlabels = plot["xticklabels"]
                        if isinstance(xlabels, str):
                            xlabels = db[xlabels]
                        row_label += ": %s" % xlabels[idx]
                    if "ylabel" in plot:
                        row_label += " (%s)" % plot["ylabel"]
                    table_content.append([row_label, '%1.2f' % value])

                    zval = (value-mean[idx])/std[idx]
                    print(row_label, value, mean[idx], std[idx], zval)
                    colour_idx = np.clip(np.floor(np.abs(zval)), 0, 2).astype(int)
                    table_colours.append([colours[3], colours[colour_idx]])

        save_page(pdf)
            
    num_cols = max([len(plots) for plots in report])

    for group_idx, plots in enumerate(report):
        # Check if we need to start a new page
        if group_idx % rows_per_page == 0:
            if group_idx > 0:
                # Format and save previous page
                save_page(pdf)
            new_page()

        # Find out how many columns the defined plots will occupy
        group_num_cols = sum([plot.get("colspan", 1) for plot in plots])
        current_col = 0

        for plot_idx, plot in enumerate(plots):
            plot = dict(plot)
            # Get the data variable to be plotted
            data_item = plot.pop("var", None)
            if data_item is None:
                print(f"WARNING: Plot variable not defined {plot}")
                continue
            data_values = np.array(db['qc_' + data_item])

            # If there are fewer plots than columns, make initial plots span an extra column
            colspan = plot.pop("colspan", 1) 
            if group_num_cols < num_cols and plot_idx < (num_cols - group_num_cols):
                colspan += 1

            # Get the axes on which to create the plot
            ax = plt.subplot2grid((rows_per_page, num_cols), (group_idx % rows_per_page, current_col), colspan=colspan)
            current_col += colspan

            # Plot the data
            seaborn.violinplot(data=data_values, scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax)
            seaborn.despine(left=True, bottom=True, ax=ax)

            # Set other properties defined for the plot. Note that some properties can take their values
            # from other data in the group JSON file
            for arg, value in plot.items():
                if arg in ["xticklabels",] and isinstance(value, str):
                    value = db[value]
                setter = getattr(ax, f"set_{arg}", None)
                if setter is not None:
                    setter(value)
                
            # Finally, if we have an individual subject's data, mark their data point on the plot with a white star
            if s_data is not None:
                subject_data = np.atleast_1d(s_data["qc_" + data_item])
                ax.scatter(range(len(subject_data)), subject_data, s=100, marker='*', c='w', edgecolors='k', linewidths=1)

    # Save last page
    save_page(pdf)
