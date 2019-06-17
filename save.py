import numpy as np
import pandas as pd
import os

# create directories, only have to do once
# seasons = [2000, 2001, 2002, 2003,2004,2005,2006,2007,2008,2009,2010,2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019]
# tours = ['PGA', 'Euro', 'Web']
# for season in seasons:
#     os.mkdir('./leaderboards/'+str(season)+'/')
#     for tour in tours:
#         os.mkdir('./leaderboards/'+str(season)+'/'+tour+'/')


# has_saved = pd.read_csv('./has_saved.csv')

# sched = pd.read_csv('./sched.csv')
# print(sched.season.unique())

new_scores = pd.read_csv('./scores.csv')

# ids = []
new_scores['tournament'] = new_scores['tournament'].str.strip()
new_scores['tournament'] = new_scores['tournament'].str.replace(" ","")
new_scores['season'] = new_scores['season'].astype(str)
new_scores['TID'] = new_scores['tournament'] + new_scores['tour'] + new_scores['season']
unique_trn= new_scores.TID.unique()
#

saved = []
for trn in unique_trn:
    leaderboard = new_scores.loc[new_scores['TID']==trn]
    season = leaderboard['season'].unique()[0]
    tour = leaderboard['tour'].unique()[0]
    tname = leaderboard['tournament'].unique()[0]
    leaderboard.to_csv('./leaderboards/'+str(season)+'/'+tour+'/'+tname+'.csv', index=False)
    saved.append([trn])

save_df = pd.DataFrame(saved,columns=['TID'])

# old save_df
has_saved = pd.read_csv('./has_saved.csv')

new_save_df = pd.concat([has_saved,save_df])
new_save_df.drop_duplicates(subset ="TID",keep='first', inplace=True)
new_save_df.to_csv('./has_saved.csv', index=False)



# end
