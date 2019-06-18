import numpy as np
import pandas as pd



saved = pd.read_csv('has_saved.csv')
sched = pd.read_csv('sched.csv')
skipped = pd.read_csv('skipped.csv')

sched = sched[:1900]

saved_ids = list(saved.TID.unique())
sched_ids = list(sched.tid.unique())
skipped_ids = list(skipped.TID.unique())

print(list(set(sched_ids)-set(skipped_ids)-set(saved_ids)))

#
