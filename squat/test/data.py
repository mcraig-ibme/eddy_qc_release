import os
import json
import random

def generate_test_data(n_subjects, outdir, sample_subject):
    for sid in range(1, n_subjects+1):
        subjdir=os.path.join(outdir, "s%i" % sid)
        os.makedirs(subjdir, exist_ok=True)
        subj_data = {}
        for k, v in sample_subject.items():
            try:
                v = v * random.normalvariate(v, v*2)
                subj_data[k] = v
            except TypeError:
                # Non numeric data - don't change
                subj_data[k] = v
        with open(os.path.join(subjdir, "qc.json"), "w") as f:
            json.dump(subj_data, f, sort_keys=True, indent=4, separators=(',', ': '))
