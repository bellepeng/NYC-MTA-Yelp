
# coding: utf-8

# In[15]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'svg'")


# In[16]:


#Import Data
tables = pd.read_csv("nyc_census_tracts.csv", usecols=[0,2,3,4,5,12,14,18,25,26])
censustract = pd.read_excel("ZIP_TRACT_032018.xlsx", header=0, usecols=[0,1])
zips = pd.read_excel('nyc_zip.xlsx', header=0)


# In[17]:


#Merge Census Data with Census Tract Key
merged_inner = pd.merge(left=tables,right=censustract, how='left', left_on='CensusTract', right_on='tract')


# In[18]:


merged_inner = merged_inner.drop_duplicates('CensusTract')


# In[19]:


#Clean up table with Neighborhoods and Zip Codes
zips = (zips.set_index(zips.columns.drop('Zips',1).tolist())
        .Zips.str.split(',', expand=True)
        .stack()
        .reset_index()
        .rename(columns={0:'Zips'})
        .loc[:, zips.columns])


# In[20]:


zips['Zips'] = pd.to_numeric(zips['Zips'])


# In[21]:


merged_inner = pd.merge(left=merged_inner,right=zips, how='left', left_on='zip', right_on='Zips')


# In[22]:


merged_inner = merged_inner.drop(['CensusTract','Men'], axis=1)


# In[23]:


#Aggregate combined table
df_agg = merged_inner.groupby(['Neighborhood']).agg({'TotalPop': 'sum', 'Women': 'sum', 'Income': 'median', 'IncomePerCap': 'mean', 'Professional': 'mean', 'Transit': 'mean'})


# In[24]:


#df_agg = df_agg.sort_values(['Professional','Income','Transit','Women'], ascending=[False, False, False, False, False])


# In[25]:


df_agg_rank = df_agg


# In[26]:


df_agg_rank['Income Rank'] = df_agg_rank['Income'].rank(ascending=False)
df_agg_rank['Professional Rank'] = df_agg_rank['Professional'].rank(ascending=False)
df_agg_rank['% Women'] = df_agg_rank['Women'] / df_agg_rank['TotalPop']
df_agg_rank['Women Rank'] = df_agg_rank['% Women'].rank(ascending=False)
df_agg_rank = df_agg_rank.drop(['Transit','TotalPop','IncomePerCap','Women'],1)


# In[27]:


df_agg_rank


# In[28]:


df_agg_rank = df_agg_rank.reset_index()
df_agg_rank[['Income Rank','Professional Rank','Women Rank','Income']] = df_agg_rank[['Income Rank','Professional Rank','Women Rank','Income']].astype(int)
#df_agg_rank[['Income Rank']] = df_agg_rank[['Income Rank']].astype(int)
df_agg_rank = df_agg_rank.sort_values(['Income Rank','Professional Rank'], ascending=[True, True])
df_agg_rank_final = df_agg_rank[['Neighborhood','Income Rank','Income','Professional Rank','Professional','Women Rank','% Women']]
df_agg_rank_final.head(5)

