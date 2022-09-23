"""
SQUAT - Individual or group report

Matteo Bastiani, FMRIB, Oxford
Martin Craig, SPMIC, Nottingham
"""
import datetime
import os
import tempfile

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import seaborn
seaborn.set()

import fsl.wrappers as fsl

RED = [0.8, 0.20, 0.20, 0.5]
AMBER = [0.91, 0.71, 0.09, 0.5]
GREEN = [0.18, 0.79, 0.22, 0.5]
NOCOLOUR = [0, 0, 0, 0]

class Report():

    def __init__(self, report_def, group_data, subject_data=None, comparison_dists={}, amber_sigma=1, red_sigma=2):
        """
        Individual or group report

        :param report_def: Dictionary definition of report, must contain key: squat_report
        :param group_data: Group QC data
        :param subject_data: Optional single-subject QC data
        :param comparison_dists: Optional dictionary for outlier flagging. Maps QC variable
                                 names to tuple of (mean, std).
        :param amber_sigma: How many std.devs away from mean to mark a value as amber
        :param red_sigma: How many std.devs away from mean to mark a value as red
        """
        self.report_def = report_def.get("squat_report", [])
        if not self.report_def:
            raise ValueError("No report definition found")
        self.group_data = group_data
        self.subject_data = subject_data
        if comparison_dists:
            self.comparison_dists = comparison_dists
        else:
            self.comparison_dists = self._get_var_dists()
        self.outlier_colours = [(red_sigma, RED), (amber_sigma, AMBER)]

        if subject_data is None:
            self.title = "SQUAT: Group report"
        else:
            self.title = f"SQUAT: Subject report {subject_data.subjid}"

        self.plot_rows_per_page = 3
        self.table_rows_per_page = 1
        self.table_columns = 2

    def save(self, fname):
        """
        Save report to file
        
        :param fname: File name
        """
        pdf = PdfPages(fname)
        self._generate(pdf)
        pdf.close()
    
    def _get_var_dists(self):
        ret = {}
        for var in self.group_data.qc_fields:
            values = self.group_data.get_data(var)
            ret[var] = np.mean(values), np.std(values) + 1e-10
        return ret

    def _get_outlier_colour(self, value, var_name):
        mean, std = self.comparison_dists[var_name]
        #mean, std = np.mean(comparison_values), np.std(comparison_values) + 1e-10
        value_sigma = np.abs((value-mean)/std)
        for sigma, colour in self.outlier_colours:
            if value_sigma > sigma:
                return colour
        return GREEN

    def _save_page(self, pdf):
        plt.tight_layout(h_pad=1, pad=4)
        plt.savefig(pdf, format='pdf')
        plt.close()

    def _new_page(self):
        plt.figure(figsize=(8.27,11.69))   # Standard portrait A4 sizes
        plt.suptitle(self.title, fontsize=10, fontweight='bold')

    def _get_data(self, vars):
        """
        Get data for a plot
        
        :param vars: Name of variable, or list of variables

        :return: Tuple of group values [NVALS, NSUBJS], subject values [NVALS] and names [NVALS]
        """
        if not isinstance(vars, list):
            vars = [vars]

        group_values, subject_values, names = [], [], []
        for var in vars:
            group_values.append(self.group_data.get_data(var))
            if self.subject_data is not None:
                subject_values.append(self.subject_data.get_data(var))
            names += [var] * group_values[-1].shape[1]

        group_values = np.concatenate(group_values, axis=1)
        if self.subject_data is not None:
            subject_values = np.concatenate(subject_values)
        else:
            subject_values = None

        return group_values, subject_values, names

    def _show_table(self, table_idx, table_title, table_content, table_colours):
        """
        Write a table to the PDF
        """
        ax = plt.subplot2grid((self.table_rows_per_page, self.table_columns), (table_idx//self.table_columns, table_idx % self.table_columns))
        ax.axis('off')
        ax.axis('tight')
        ax.set_title(table_title, fontsize=12, fontweight='bold',loc='left')
        c1len = max([len(str(c[0])) for c in table_content])
        c2len = max([len(str(c[1])) for c in table_content])
        col_prop = c1len / (c1len+c2len)
        tb = ax.table(
            cellText=table_content, 
            cellColours=table_colours,
            loc='upper center',
            cellLoc='left',
            colWidths=[col_prop, 1-col_prop],
        )
        tb.auto_set_font_size(True)
        tb.scale(1, 2)

    def _generate_subject_tables(self, pdf):
        """
        Generate tables for subject report including RAG flagging of outliers
        """
        table_idx, table_title, table_content, table_colours = 0, None, [], []
        for group_idx, plots in enumerate(self.report_def):
            for plot_idx, plot in enumerate(plots):
                plot = dict(plot)
                if plot.get("type", "dist") != "dist":
                    continue

                new_table_title = plot.get("table_title", table_title)
                if new_table_title != table_title:
                    if table_title is not None and len(table_content) > 0:
                        # We have a previous table - display this first
                        if table_idx % (self.table_rows_per_page*self.table_columns) == 0:
                            if table_idx > 0: self._save_page(pdf)
                            self._new_page()
                        self._show_table(table_idx, table_title, table_content, table_colours)
                        table_idx += 1
                        table_content = []
                        table_colours = []
                    table_title = new_table_title

                # Get the data variable and add all values to the table with appropriate label
                vars = plot.pop("var", None)
                if vars is None:
                    print(f"WARNING: No variables defined for plot {plot}")
                    continue

                xlabels = None
                if "xticklabels" in plot:
                    xlabels = plot["xticklabels"]
                    if isinstance(xlabels, str):
                        if xlabels in self.group_data:
                            xlabels = self.group_data[xlabels]
                        else:
                            xlabels = None

                group_values, data_values, var_names = self._get_data(vars)
                for idx, value in enumerate(data_values):
                    row_label = plot.get("title", "")
                    if xlabels:
                        row_label += ": %s" % xlabels[idx]
                    if "ylabel" in plot:
                        row_label += " (%s)" % plot["ylabel"]
                    table_content.append([row_label, '%1.2f' % value])
                    table_colours.append([NOCOLOUR, self._get_outlier_colour(value, var_names[idx])])

        # Show last table
        if table_title is not None and len(table_content) > 0:
            self._show_table(table_idx, table_title, table_content, table_colours)
        self._save_page(pdf)

    def _generate_group_plots(self, pdf):
        """
        Generate plots from group data

        Plots are arranged in groups, each of which is a row on the page. Plots
        are either image plots, line plots (for single subject report only) or distribution plots
        (for individual and group reports)
        """
        num_cols = max([len(group) for group in self.report_def])

        current_row = 0
        for group in self.report_def:
            # Check if we need to start a new page
            if current_row % self.plot_rows_per_page == 0:
                if current_row > 0:
                    # Format and save previous page
                    self._save_page(pdf)
                self._new_page()

            # Find out how many columns the defined plots will occupy
            group_num_cols = sum([plot.get("colspan", 1) for plot in group])
            current_col = 0

            # If there are fewer plots than columns, make initial plots span extra columns
            extra_cols = num_cols - group_num_cols
            num_plots = len(group)
            for plot_idx in range(extra_cols):
                group[plot_idx % num_plots]["colspan"] = group[plot_idx % num_plots].pop("colspan", 1) + 1

            group_any_plotted = False
            for plot in group:
                plot = dict(plot)
                # Get the axes on which to create the plot
                colspan = plot.pop("colspan", 1)
                ax = plt.subplot2grid((self.plot_rows_per_page, num_cols), (current_row % self.plot_rows_per_page, current_col), colspan=colspan)
                plotted = self._do_plot(ax, plot)

                if plotted:
                    current_col += colspan
                    group_any_plotted = True
            if group_any_plotted:
                current_row += 1

        # Save last page
        self._save_page(pdf)

    def _do_plot(self, ax, plot):
        # Get the data variable or image to be plotted
        plot_type = plot.pop("type", "dist")
        if plot_type == "dist":
            plotted = self._distribution_plot(ax, plot)
        elif plot_type == "img":
            plotted = self._image_plot(ax, plot)
        elif plot_type == "line":
            plotted = self._line_plot(ax, plot)

        # Set other properties defined for the plot. Note that some properties can take their values
        # from other data in the group JSON file
        if plotted:
            for arg, value in plot.items():
                if arg in ["xticklabels",] and isinstance(value, str):
                    if value in self.group_data:
                        value = self.group_data[value]
                    else:
                        value = None
                setter = getattr(ax, f"set_{arg}", None)
                if setter is not None:
                    setter(value)
        return plotted

    def _line_plot(self, ax, plot):
        """
        Line plot for subject reports only
        """
        if self.subject_data is None:
            return False
        data_item = plot.pop("var", None)
        if not data_item:
            print(f"WARNING: plot variable not defined for line plot: {plot}")
            return False
        group_values, subject_values, var_names = self._get_data(data_item)
        if subject_values is None or len(subject_values) == 0:
            # Skip plot if data could not be found
            return False
        ax.plot(subject_values)
        return True

    def _image_plot(self, ax, plot):
        """
        Plot images for subject reports only
        """
        if self.subject_data is None:
            return False
        img_name = plot.pop("img", None)
        if not img_name:
            print(f"WARNING: image name not defined for image plot: {plot}")
            return False
        img = self.subject_data.get_image(img_name)
        if not img:
            return False

        with tempfile.TemporaryDirectory() as tempdir:
            if ".nii" in img:
                slice_img_fname = os.path.join(tempdir, "slice.png")
                fsl.slicer(img, i="0 1", a=slice_img_fname)
            else:
                slice_img_fname = img

            slice_img = matplotlib.image.imread(slice_img_fname)
            ax.imshow(slice_img.data, interpolation='none')
            #plt.colorbar(im, ax=ax)
            ax.grid(False)
            ax.axis('off')
            #ax.set_title(title)
        return True

    def _distribution_plot(self, ax, plot):
        """
        Plot the distribution of data variable(s)
        """
        data_item = plot.pop("var", None)
        if not data_item:
            print(f"WARNING: plot variable not defined for distribution plot: {plot}")
            return False

        group_values, subject_values, var_names = self._get_data(data_item)
        if group_values is None or len(group_values) == 0:
            # Skip plot if data could not be found
            return False

        # Plot the data
        seaborn.violinplot(data=group_values, scale='width', width=0.5, palette='Set3', linewidth=1, inner='point', ax=ax)
        seaborn.despine(left=True, bottom=True, ax=ax)
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        #ax.ticklabel_format(style='plain')

        # Finally, if we have an individual subject's data, mark their data point on the plot with a white star
        if self.subject_data is not None:
            ax.scatter(range(len(subject_values)), subject_values, s=100, marker='*', c='w', edgecolors='k', linewidths=1)
        return True

    def _generate(self, pdf):
        """
        Generate group report pdf that contains:
        - Value tables where we have single subject data
        - violin plots for outlier distributions
        
        :param pdf: PdfPages object
        """
        if self.subject_data is not None:
            self._generate_subject_tables(pdf)

        self._generate_group_plots(pdf)
        
        # Set the file's metadata via the PdfPages object:
        d = pdf.infodict()
        d['Title'] = 'SQUAT QC report'
        d['Author'] = u'SQUAT'
        d['Subject'] = self.title
        d['Keywords'] = 'QC'
        d['CreationDate'] = datetime.datetime.today()
        d['ModDate'] = datetime.datetime.today()
