
# coding: utf-8

# In[12]:


import pandas as pd
import os
import json
from pprint import pprint
from pandas import DataFrame, Series


# In[14]:


os.chdir('/Users/bellepeng/Desktop/Metis/github/project_benson/Yelp')
get_ipython().system(u'pwd')


# ## Extract Yelp Data

# In[15]:


def read_yelp(filename):
    zip_list = []
    name_list = []
    price_list = []
    rating_list = []
    review_ct_list = []
    lat=[]
    long=[]
    
    with open(filename, 'r') as myfile:
        data=json.loads(myfile.read())
        Arr=data['businesses']

        for j in range(len(Arr)):
            if not Arr[j]['location']['zip_code']: zip_code=None
            else: zip_code=Arr[j]['location']['zip_code']
            zip_list.append(zip_code)

            if not Arr[j]['coordinates']['latitude']: latitude=None
            else: latitude=Arr[j]['coordinates']['latitude']
            lat.append(latitude)

            if not Arr[j]['coordinates']['longitude']: longitude=None
            else: longitude=Arr[j]['coordinates']['longitude']
            long.append(longitude)

            if not Arr[j]['name']: name=None
            else: name=Arr[j]['name']
            name_list.append(name)

            if 'price' not in Arr[j]: price=None
            else: price=Arr[j]['price']
            price_list.append(price)

            if not Arr[j]['rating']: rating=None
            else: rating=Arr[j]['rating']
            rating_list.append(rating)

            if not Arr[j]['review_count']: review_count=None
            else: review_count=Arr[j]['review_count']
            review_ct_list.append(review_count)

            yelpMaster={'name': name_list, 
                        'zip_code': zip_list,
                        'price': price_list,
                        'rating': rating_list,
                        'review_count': review_ct_list,
                        'latitude': lat,
                        'longitude': long
                       }
    dfi=DataFrame(yelpMaster)
    return dfi


# In[16]:


read_yelp('yelp19.json').head(5)


# In[17]:


for i in range(1,21):
    filename=("yelp"+str(i)+".json")
    print(filename)
    dfi=read_yelp(filename)
    
    if i==1: df=dfi
    else: df=pd.concat([df, dfi])
    
    print(df.shape)

df.head(5)


# __Data Quality Check__

# In[18]:


# df[df['name']=="The Halal Guys"]
df[df['name']=="Peter Luger"]


# In[19]:


df.sort_values('review_count', ascending = False).head(5)


# In[20]:


df.loc[(df['price']=='$$$$')].head(5)


# In[21]:


df.loc[df['name']=='Morimoto']['price']


# In[22]:


length=df['price'].apply(lambda x: (x and len(x)))
length.value_counts()


# __Define New Vars__

# In[23]:


# Define the Expensive Restaurants
df['is_expensive'] = df['price'].apply(lambda x: (x and (x[:3] == '$$$')))
df.sort_values('is_expensive', ascending=True, inplace=True)
df.head()


# In[24]:


df.tail()


# In[25]:


df[(df['price']=='$$$$')].head()


# In[26]:


# Define the Popular Restaurants
df['is_popular'] = df['review_count'].apply(lambda x: (x>=1000))
df.sort_values('is_popular', ascending=True, inplace=True)
df.head(5)


# In[27]:


df.tail(5)


# __De-Dup repeated records__

# In[28]:


df2=df.drop_duplicates(keep='first')
df2.head()
df2.shape


# In[29]:


df.loc[df['name']=='Momofuku Ko']


# In[30]:


df2.loc[df2['name']=='Momofuku Ko']


# #### If I want to save it as CSV and read it back 
# df.to_csv('Yelp.csv')  
# df_in=pd.read_csv('Yelp.csv')  
# df_in.head(10)  
# df_in.drop('Unnamed: 0', axis=1, inplace=True)  
# df_in.head(10) 
#   
# _Merge Example:_  
# result = pd.merge(left, right, on='key')

# __Add in Neighborhood Names__

# In[47]:


os.chdir('/Users/bellepeng/Desktop/Metis/github/project_benson')
get_ipython().system(u'pwd')


# In[32]:


zips=pd.read_csv('nyc_zip.csv')
zips.head()


# In[33]:


zips = (zips.set_index(zips.columns.drop('Zips',1).tolist())
   .Zips.str.split(',', expand=True)
   .stack()
   .reset_index()
   .rename(columns={0:'Zips'})
   .loc[:, zips.columns]
)
zips.head()


# In[34]:


zips.rename(columns={'Zips': 'zip_code'}, inplace=True)
zips.head()


# In[35]:


zips['zip_code']=zips['zip_code'].astype(str).str.strip()
df['zip_code']=df['zip_code'].str.strip()


# In[36]:


df3 = pd.merge(df2, zips, how='left', on='zip_code')
df3.head()


# __Merge to Station Names__

# In[52]:


stations=pd.read_csv('zipcode (1).csv')
stations.head()


# In[53]:


df2_5=df3


# In[62]:


stations['zip_code']=stations['zip_code'].astype(str).str.strip()
df2_5['zip_code']=df2_5['zip_code'].str.strip()


# In[66]:


df3 = pd.merge(df2_5, stations, how='right', on='zip_code')
df3.loc[pd.isnull(df3['station'])]


# ### Analyze by Zip
# __Questions I want to answer__
# - Which zip has the most restaurants?
# - Which zip has the most popular resturants?
# - Which zip has the most expensive restaurants?

# In[37]:


df3['price'].value_counts()
df3['price'].value_counts()/(df3.shape[0])


# __Top Zips with restaurants__

# In[67]:


def yelp_stats(topzips):
    df3_sub=df3.loc[df3['zip_code'].apply(lambda x: x in topzips)]
    print("Number of restaurants in these zips: "+ str(df3_sub.shape[0]))
    
    # The Top zips with the most restaurants
    df3_sub_most_rest=df3_sub.groupby(['zip_code', 'station', 'Neighborhood']).review_count.agg(['count'])
    df3_sub_most_rest.rename(columns={'count': 'num_of_restaurants'}, inplace=True)
    df3_sub_most_rest['num_of_restaurants'].sum()
    df3_sub_most_rest.sort_values('num_of_restaurants', ascending = False, inplace=True)
    
    # The Top zips with the most POPULAR restaurants
    df3_sub_popular=df3_sub.groupby(['zip_code', 'station', 'Neighborhood']).is_popular.agg(['sum'])
    df3_sub_popular.rename(columns={'sum': 'num_of_popular_rest'}, inplace=True)
    df3_sub_popular.sort_values('num_of_popular_rest', ascending = False, inplace=True)
    
    # The Top zips with the most EXPENSIVE restaurants
    df3_sub_exp=df3_sub.groupby(['zip_code', 'station', 'Neighborhood']).is_expensive.agg(['sum'])
    df3_sub_exp.rename(columns={'sum': 'num_of_expensive_rest'}, inplace=True)
    df3_sub_exp.sort_values('num_of_expensive_rest', ascending = False, inplace=True)
    
    return {"The most Restaurants": df3_sub_most_rest, 
            "Most Popular Restaurants": df3_sub_popular,
            "Most Expensive Restaurants": df3_sub_exp
           }


# In[68]:


topzips=['10119', '10018', '11003', '10003', '10010', '10038', '10028', '10035', 
         '10023', '10013', '10065', '10025', '10020', '11354', '10011', '10001',
         '11373'
        ]
results=yelp_stats(topzips)


# In[69]:


results['The most Restaurants']


# In[70]:


results['Most Popular Restaurants']


# In[71]:


results['Most Expensive Restaurants']


# In[137]:


pop_rest=pd.DataFrame(results['Most Popular Restaurants'])
pop_rest=pop_rest.reset_index()
pop_rest.head()


# In[138]:


exp_rest=pd.DataFrame(results['Most Expensive Restaurants'])
exp_rest=exp_rest.reset_index()
exp_rest.head()


# In[142]:


pop_rest.drop_duplicates(keep='first', subset=['zip_code', 'num_of_popular_rest'], inplace=True)
pop_rest.head()


# In[143]:


exp_rest.drop_duplicates(keep='first', subset=['zip_code', 'num_of_expensive_rest'], inplace=True)
exp_rest.head()


# In[150]:


pop_exp_rest = pd.merge(left=pop_rest, right=exp_rest, how='outer', on=['zip_code', 'station', 'Neighborhood'])
pop_exp_rest.set_index('zip_code', inplace=True)
pop_exp_rest.head(3)


# __Graphing__

# In[86]:


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')


# In[178]:


# Plot Popular Restaurants by Zip Code
pop_exp_rest2=pop_exp_rest.sort_values('num_of_popular_rest', ascending = False)
plt.style.use("seaborn")
ax = pop_exp_rest2['num_of_popular_rest'].head(5).plot(kind='bar', rot=0, 
                    title ="Zip Codes with the most Popular Restaurants", 
                    figsize=(8, 8), fontsize=15, legend=False)
ax.set_xlabel("", fontsize=15)
ax.title.set_size(18)
ax.set_ylabel("# Restaurants with > 1000 Reviews", fontsize=15)
# ax.legend(["Zips w/ the most Popular restaurants"], fontsize=15);
plt.show()


# In[180]:


pop_exp_rest2=pop_exp_rest.sort_values('num_of_expensive_rest', ascending = False)
plt.style.use("seaborn")
ax = pop_exp_rest2['num_of_expensive_rest'].head(8).plot(kind='bar', rot=0, 
                    title ="Zip Codes with the most Expensive Restaurants", 
                    figsize=(8, 8), fontsize=15, legend=False)
ax.set_xlabel("", fontsize=15)
ax.title.set_size(18)
ax.set_ylabel("# Restaurants with > $$$ ", fontsize=15)
plt.show()


# In[181]:


pop_exp_rest2=pop_exp_rest.sort_values(['num_of_expensive_rest', 'num_of_popular_rest'], ascending = False)
plt.style.use("seaborn")
ax = pop_exp_rest2.head(5).plot(kind='bar', rot=0, 
                        title ="Zip Codes with the most Expensive Restaurants", 
                        figsize=(8, 8), fontsize=15, legend=False)
ax.set_xlabel("", fontsize=15)
ax.set_ylabel("# Restaurants with > $$$ ", fontsize=15)
ax.title.set_size(18)
ax.legend(["Popular", "Expensive"], fontsize=15);
plt.show()


# In[ ]:





# __Which restaurants are in these stations?__

# In[246]:


# stations=['34 ST-PENN STA', 'TWENTY THIRD ST', '14 ST-UNION SQ']
stations=['14 ST-UNION SQ']


# In[247]:


target=df3.loc[df3['station'].apply(lambda x: x in stations)]
target.sort_values(['review_count'], ascending = False, inplace=True)
target.head()


# In[225]:


target.groupby('station')['review_count'].nlargest(5)