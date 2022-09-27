"""
SQUAT: Study-wise QUality Assessment Tool

Useful functions for extracting data from EDDY run

Matteo Bastiani, Michiel Cottaar, Jesper Andersson, FMRIB, Oxford
"""

import numpy as np
import logging

LOG = logging.getLogger(__name__)

def round_bvals_median(bvals, tol=100):
    """
    Round bvals to the median value for each identified shell
    """
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
        LOG.info('Found b-shell of %i orientations with b-value %f' % (nuse, median_b))
        res_b[use] = median_b
        selected[use] = True
    res_b[res_b <= tol] = 0
    return res_b

def round_bvals(bvals):
    """
    Round bvals to nearest 100
    """
    return np.round(bvals, decimals=-2)
