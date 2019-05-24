import numpy as np
import pandas as pd

df = pd.read_csv('./sched.csv')

print(df.groupby(['season','tour']).count())

#
