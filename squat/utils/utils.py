#!/usr/bin/env python
"""Useful functions."""

import numpy as np
import sys
import pkg_resources



#=========================================================================================
# Matteo Bastiani, Michiel Cottaar, Jesper Andersson
# 01-06-2017, FMRIB, Oxford
#=========================================================================================

def round_bvals(bvals):
    # Round the bvals to the median value for each identified shell
    tol = 100   # Tolerance
    selected = np.zeros(bvals.size, dtype='bool')
    same_b = abs(bvals[:, None] - bvals[None, :]) <= tol
    res_b = bvals.copy()
    while not selected.all():
        use = np.zeros(selected.size, dtype='bool')
        use[np.where(~selected)[0][0]] = True
        nuse = 0
        while (use.sum() != nuse):
            nuse = use.sum()
            use = same_b[use].any(0)
            if (use & selected).any():
                raise ValueError('Re-using the same indices (%s)' % str(np.where(use & selected))[0])
        median_b = int(np.median(bvals[use]))
        print('found b-shell of %i orientations with b-value %f' % (nuse, median_b))
        res_b[use] = median_b
        selected[use] = True
    res_b[res_b <= tol] = 0
    return res_b

class EddyCommand(object):
    """ The purpose of this class is to read the files that eddy generates
        to describe how it was run and to provide information about that,
        and related information, to the programmer
    """

    def __init__(self, basename='', tool='', verbose=False):
        version = pkg_resources.require("eddy_qc")[0].version
        
        self._eddy_papers = {}
        self._eddy_papers["qc"] = '\nMatteo Bastiani, Michiel Cottaar, Sean P. Fitzgibbon, Sana Suri, Fidel Alfaro-Almagro, Stamatios N. Sotiropoulos, Saad Jbabdi and Jesper L.R. Andersson. 2019. ' \
                                   'Automated quality control for within and between studies diffusion MRI data using a non-parametric framework for movement and distortion correction. ' \
                                   'NeuroImage 184:801-812'
        self._eddy_papers["topup"] = '\nJesper L.R. Andersson, Stefan Skare and John Ashburner. 2003. ' \
                                     'How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging. ' \
                                     'NeuroImage 20:870-888'
        self._eddy_papers["any"] = '\nJesper L.R. Andersson and Stamatios N. Sotiropoulos. 2016. ' \
                                   'An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. ' \
                                   'NeuroImage 125:1063-1078'
        self._eddy_papers["repol"] = '\nJesper L.R. Andersson, Mark S. Graham, Eniko Zsoldos and Stamatios N. Sotiropoulos. 2016. ' \
                                     'Incorporating outlier detection and replacement into a non-parametric framework for movement and distortion correction of diffusion MR images. ' \
                                     'NeuroImage 141:556-572'
        self._eddy_papers["mporder"] = '\nJesper L.R. Andersson, Mark S. Graham, Ivana Drobnjak, Hui Zhang, Nicola Filippini and Matteo Bastiani. 2017. ' \
                                       'Towards a comprehensive framework for movement and distortion correction of diffusion MR images: Within volume movement. ' \
                                       'NeuroImage 152:450-466'
        self._eddy_papers["estimate_move_by_susceptibility"] = '\nJesper L.R. Andersson, Mark S. Graham, Ivana Drobnjak, Hui Zhang and Jon Campbell. 2018. ' \
                                                               'Susceptibility-induced distortion that varies due to motion: Correction in diffusion MR without acquiring additional data. ' \
                                                               'NeuroImage 171:277-295'

        self._eddy_refs = {}
        self._eddy_refs["qc"] = '(Bastiani et al., 2019)'
        self._eddy_refs["topup"] = '(Andersson et al., 2003)'
        self._eddy_refs["any"] = '(Andersson & Sotiropoulos, 2016)'
        self._eddy_refs["repol"] = '(Andersson et al., 2016)'
        self._eddy_refs["mporder"] = '(Andersson et al., 2017)'
        self._eddy_refs["estimate_move_by_susceptibility"] = '(Andersson et al., 2018)'

        if len(basename) > 0:
            self._command_fname = basename + '.eddy_command_txt'
            self._param_fname = basename + '.eddy_values_of_all_input_parameters'
            try:
                self._command = ''
                fp = open(self._command_fname, 'r')
            except IOError:
                if verbose:
                    print('Warning: Cannot open', self._command_fname)
            else:
                self._command = fp.readline()
            try:
                self._parameters = {}
                fp = open(self._param_fname, 'r')
            except IOError:
                if verbose:
                    print('Warning: Cannot open', self._param_fname)
            else:
                for cline in fp:
                    if cline.find('--') == 0:
                        self._parameters[cline[2:cline.find('=')]] = cline[cline.find('=') + 1:].strip()
        else:
            self._command_fname = ''
            self._param_fname = ''
            self._command = ''
            self._parameters = {}

        if tool == 'squad':
            self._tool = 'Group QC report generated using eddy squad v' + str(version)
        elif tool == 'quad':
            self._tool = 'Single subject QC report generated using eddy quad v' + str(version)

    def Tool(self):
        return self._tool

    def KnowsParameters(self):
        if len(self._parameters):
            return True
        return False
    
    def GetParameters(self):
        if len(self._parameters):
            return self._parameters
        return False

    def ParameterValue(self,param):
        if param in self._parameters:
            return self._parameters[param]
        else:
            raise Exception('Parameter ' + param + ' does not exist or its value is not known')

    def Paper(self,param):
        if param in self._eddy_papers:
            return self._eddy_papers[param]
        else:
            raise Exception('No paper for parameter ' + param)

    def RefInText(self,param):
        if param in self._eddy_refs:
            return self._eddy_refs[param]
        else:
            raise Exception('No ref for parameter ' + param)

    def MethodsText(self):
        if len(self._parameters) > 0: # If eddy 6.0.1 or later was used
            text_in_methods = self.Tool() + '\n\n' \
                              'When using eddy and its QC tools, we ask you to please reference the papers describing the different aspects ' \
                              'of the modelling and corrections. The following suggestion for a methods section and list of ' \
                              'references has been tailored for you based on your eddy command line.\n\nMETHODS\n'
            text_in_refs = 'REFERENCES'
            if self.ParameterValue('topup'):
                text_in_methods = text_in_methods + 'The susceptibility induced off-resonance field was estimated from ' \
                                                    'spin-echo EPI images acquired with different phase-encode directions ' \
                                                    + self.RefInText('topup') + '. This field was passed to "eddy", a tool that ' \
                                                    'combined it with estimating gross subject movement and eddy current-' \
                                                    'induced distortions ' + self.RefInText('any') + '.The quality of the dataset was assessed using ' \
                                                    'the eddy QC tools ' + self.RefInText('qc') + '.'
                text_in_refs = text_in_refs + self.Paper('topup') + '\n' + self.Paper('any') + '\n' + self.Paper('qc')
            else:
                text_in_methods = text_in_methods + 'Eddy current-induced distortions and gross subject movement were corrected using the ' \
                                                    '"eddy" tool ' + self.RefInText('any') + '. The quality of the dataset was assessed using ' \
                                                    'the eddy QC tools ' + self.RefInText('qc') + '.'
                text_in_refs = text_in_refs + self.Paper('any') + '\n' + self.Paper('qc')
            if self.ParameterValue('repol') == 'True':
                text_in_methods = text_in_methods + ' Slices with signal loss caused by subject movement coinciding with the ' \
                                                    'diffusion encoding were detected and replaced by predictions made by a ' \
                                                    'Gaussian Process ' + self.RefInText('repol') + '.'
                text_in_refs = text_in_refs + '\n' + self.Paper('repol')
            if int(self.ParameterValue('mporder')) > 0:
                text_in_methods = text_in_methods + ' Intra-volume subject movement, leading to disjoint slices that when stacked ' \
                                                    'does not amount to a valid volumetric representation of the object, was ' \
                                                    'corrected using slice-to-volume alignment ' + self.RefInText('mporder') + '.'
                text_in_refs = text_in_refs + '\n' + self.Paper('mporder')
            if self.ParameterValue('estimate_move_by_susceptibility') == 'True':
                text_in_methods = text_in_methods + ' Changes to the susceptibility-induced distortions caused by subject movement ' \
                                                    'was estimated directly from the data using a Taylor expansion, with respect to ' \
                                                    'pitch and roll, around the first volume of the data set ' + \
                                                    self.RefInText('estimate_move_by_susceptibility') + '.'
                text_in_refs = text_in_refs + '\n' + self.Paper('estimate_move_by_susceptibility')
        else: # If eddy 6.0.0 or earlier was used
            text_in_methods = self.Tool() + '\n\n' \
                              'When using eddy and its QC tools, we ask you to please reference the papers describing the different aspects ' \
                              'of the modelling and corrections. The ' + self.RefInText('any') + ' paper is the main eddy ' \
                              'reference and should always be be cited when using eddy. The ' + self.RefInText('qc') + ' paper is the main eddy ' \
                              'QC reference and should always be be cited when using the QC tools. When using topup to estimate a fieldmap ' \
                              'prior to running eddy one should also cite ' + self.RefInText('topup') + '. If you have used eddy to ' \
                              'detect and replace outlier slices (by adding --repol to the eddy command line), please also cite ' \
                              + self.RefInText('repol') + '. If eddy was used to estimate and correct for intra-volume (slice-to-vol) ' \
                              'movement by specifying --mporder, please also cite ' + self.RefInText('mporder') + '. Finally, if you ' \
                              'asked eddy to model how the susceptibility-induced distortions change as a consequence of subject ' \
                              'movement (with the --estimate_move_by_susceptibility flag), please cite ' \
                              + self.RefInText('estimate_move_by_susceptibility') + '.'
            text_in_refs = '\nREFERENCES\n' + self.Paper('topup') + '\n' + self.Paper('any') + '\n' + self.Paper('repol') + \
                           '\n' + self.Paper('mporder') + '\n' +  self.Paper('estimate_move_by_susceptibility') + '\n' +  self.Paper('qc')

        return text_in_methods + '\n\n' + text_in_refs
