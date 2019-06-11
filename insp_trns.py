import numpy as np
import pandas as pd

trn_df = pd.read_csv('./scores.csv')

sched_df = pd.read_csv('./sched.csv')
# testing
sched_df = sched_df[:50]

trn_df['tournament'] = trn_df['tournament'].str.strip()
trn_df['season'] = trn_df['season'].astype(str)
trn_df['TID'] = trn_df['tournament'] + trn_df['tour'] + trn_df['season']

sched_df['name'] = sched_df['name'].str.strip()
sched_df['season'] = sched_df['season'].astype(str)
sched_df['TID'] = sched_df['name'] + sched_df['tour'] + sched_df['season']

unique_trn= trn_df.TID.unique()
unique_sched = sched_df.TID.unique()

print(list(set(unique_sched) - set(unique_trn)))

#
