import numpy as np
import pandas as pd
import pickle


#  Download MTA data from March 2018 - May 2018
def compile_df():
    dates = [303, 310, 317, 324, 331, 407, 414, 421, 428, 505, 512, 519, 526, 602]
    date_urls = ["http://web.mta.info/developers/data/nyct/turnstile/turnstile_180{}.txt".format(date) for date in dates]
    df = pd.concat([pd.read_csv(url) for url in date_urls])
    pickle.dump(df, open("mta.pickle", "wb"))
    return df


#  Compile dataframe & clean columns
df = compile_df()
df.columns = [col.strip() for col in df.columns]

#  Drop the RECOVR AUD entries
df = df[df.DESC == 'REGULAR']

#  Combine DATE & TIME columns into DATETIME formatted column
df['DATETIME'] = pd.to_datetime(df.DATE+" "+df.TIME, format='%m/%d/%Y %H:%M:%S')

#  Check duplicates -- looks fine because we dropped RECOVR AUD
df.groupby(['C/A',
            'UNIT',
            'SCP',
            'STATION',
            'DATETIME']).ENTRIES.count().reset_index().sort_values("ENTRIES", ascending=False).head()


#  Find the most populated station
dailycount = df.groupby(['C/A',
                         'UNIT',
                         'SCP',
                         'STATION',
                         'DATE'])['ENTRIES', 'EXITS'].first().reset_index()

dailycount[['PREVDATE',
            'PREVENTRIES',
            'PREVEXITS']] = dailycount.groupby(['C/A',
                                                'UNIT',
                                                'SCP',
                                                'STATION',
                                                'STATION'])['DATE',
                                                            'ENTRIES',
                                                            'EXITS'].transform(lambda x: x.shift(1))

dailycount.dropna(subset=['PREVDATE'], inplace=True)
dailycount['ENTRIES_DIFF'] = dailycount['ENTRIES'] - dailycount['PREVENTRIES']
dailycount['EXITS_DIFF'] = dailycount['EXITS'] - dailycount['PREVEXITS']
dailycount['DIFF'] = dailycount['ENTRIES_DIFF'] + dailycount['EXITS_DIFF']


#  Adjust for outliers (drop negatives and greater than 1 million)
daily = dailycount[(dailycount.DIFF > 0 ) & (dailycount.DIFF < 1000000)]


#  And the most populated stations are...
mostpopular = daily.groupby(['STATION'])['STATION', 'DIFF'].sum().reset_index()
print("The most populated stations, in decreasing order: \n")
print(mostpopular.sort_values('DIFF', ascending=False))
