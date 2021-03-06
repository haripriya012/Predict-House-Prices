#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.stats import norm
from sklearn.preprocessing import StandardScaler
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
get_ipython().run_line_magic('matplotlib', 'inline')
warnings.filterwarnings('ignore')

#Models for Prediction problem
from sklearn.linear_model import LinearRegression, Lasso, ElasticNet,Ridge, BayesianRidge, LassoLarsIC
from sklearn.kernel_ridge import KernelRidge
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from scipy.stats import skew #Function to Determine skewness associated with variables in the data
from scipy.stats.stats import pearsonr #To find Correlation coefficient
from sklearn.preprocessing import LabelEncoder
import warnings 
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.metrics import explained_variance_score
from sklearn.metrics import mean_squared_error, mean_squared_log_error 
from sklearn.preprocessing import PolynomialFeatures,StandardScaler
#train 
df_train = pd.read_csv('train.csv')

#summary
df_train.columns
df_train['SalePrice'].describe()
f, ax = plt.subplots(nrows = 1, ncols = 1,figsize=(12, 8))
fig = sns.boxplot(x="OverallQual", y="SalePrice", data=df_train)
fig.axis(ymin=0, ymax=1000000);

corrmat = df_train.corr()
f, ax = plt.subplots(figsize=(12, 9))
sns.heatmap(corrmat, vmax=.8, square=True);
missing_data = df_train.isnull().apply(sum).sort_values(ascending = False)
missing_col_name = missing_data[missing_data > 0]
print(missing_col_name)
print("There are {} variables with missing values".format(len(missing_col_name)))

test = pd.read_csv('test.csv')
fulldata = pd.concat([df_train,test])
fulldata = fulldata.reset_index(drop = True)
fulldata_missing = fulldata.isnull().sum().sort_values(ascending = False)
fulldata_missing_colname = fulldata_missing[fulldata_missing > 0]
print(fulldata_missing_colname)
NoneFill = ["PoolQC","MiscFeature","Alley","Fence","FireplaceQu","GarageType", "GarageFinish", "GarageQual", "GarageCond","BsmtQual", "BsmtCond", "BsmtExposure", "BsmtFinType1", "BsmtFinType2","MasVnrType"]

for item in NoneFill:
    fulldata[item] = fulldata[item].fillna("None")
    
#These categorical Labels already are in numeric categorical form and hence do not require encoding, however, conversion to dummy variables can be done
ZeroFill = ['GarageYrBlt', 'GarageArea', 'GarageCars','BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF','TotalBsmtSF', 'BsmtFullBath', 'BsmtHalfBath','MasVnrArea']

for item in ZeroFill:
    fulldata[item] = fulldata[item].fillna(0)

fulldata["LotFrontage"] = fulldata.groupby("Neighborhood")["LotFrontage"].transform(lambda x: x.fillna(x.median()))

ModeFill = ['MSZoning','Electrical','KitchenQual','Exterior1st','Exterior2nd','SaleType','Utilities']

for item in ModeFill:
    fulldata[item] = fulldata[item].fillna(fulldata[item].mode()[0])
fulldata.drop("SalePrice", axis = 1, inplace = True)
fulldata.isnull().any().any()

df_train["SalePrice"] = np.log1p(df_train["SalePrice"])

y_train = df_train.SalePrice.values

#splitting the data to train the model
x_train = fulldata[:df_train.shape[0]]

print("x_train shape:{}".format(x_train.shape))
print("y_train shape:{}".format(y_train.shape))

#plots to visualize GrLivArea Outlier
f, ax = plt.subplots()
ax.scatter(x = df_train["GrLivArea"],y = df_train["SalePrice"])
ax.set_xlabel("Ground Living Area")
ax.set_ylabel("Sale Price")

#Plot to Visualize TotalBsmtSF outlier
f,ax = plt.subplots()
ax.scatter(x = df_train["TotalBsmtSF"], y = df_train["SalePrice"])
ax.set_xlabel("Total basement Square feet")
ax.set_ylabel("Sale Price")

TotalBsmtSF_row = df_train.loc[(df_train["TotalBsmtSF"] > 6000) & (df_train["SalePrice"] < 200000)]
GrLivArea_row = df_train.loc[(df_train['GrLivArea'] > 4000) & (df_train['SalePrice'] < 200000)]
TotalBsmtSF_row
GrLivArea_row


#Remving the outliers from both the dataset - kindly note to follow the same order while removing the oulier.
#1st remove the outlier from fulldata dataset then remove from train dataset
#Because once you remove the outlier from train data, you wont get the index to remove it from fulldata.
fulldata = fulldata.drop(df_train[(df_train['GrLivArea']>4000) & (df_train['SalePrice']<200000)].index)
fulldata = fulldata.reset_index(drop = True)
train = df_train.drop(df_train[(df_train['GrLivArea']>4000) & (df_train['SalePrice']<200000)].index)
train = df_train.reset_index(drop = True)


print("Merged Full Data Shape:{}".format(fulldata.shape))
print("-"*160)
print("Training Data Shape:{}".format(train.shape))
print("-"*160)
print("Test Data Shape:{}".format(test.shape))
fulldata['MSSubClass'] = fulldata['MSSubClass'].apply(str)


#Changing OverallCond into a categorical variable
fulldata['OverallCond'] = fulldata['OverallCond'].astype(str)


#Year and month sold are transformed into categorical features.
fulldata['YrSold'] = fulldata['YrSold'].astype(str)
fulldata['MoSold'] = fulldata['MoSold'].astype(str)
fulldata['YearBuilt'] = fulldata['YearBuilt'].astype(str)
fulldata['YearRemodAdd'] = fulldata["YearRemodAdd"].astype(str)
fulldata['TotalSF'] = fulldata['TotalBsmtSF'] + fulldata['1stFlrSF'] + fulldata['2ndFlrSF']

cols = ('FireplaceQu', 'BsmtQual', 'BsmtCond', 'GarageQual', 'GarageCond', 
        'ExterQual', 'ExterCond','HeatingQC', 'PoolQC', 'KitchenQual', 'BsmtFinType1', 
        'BsmtFinType2', 'Functional', 'Fence', 'BsmtExposure', 'GarageFinish', 'LandSlope',
        'LotShape', 'PavedDrive', 'Street', 'Alley', 'CentralAir', 'MSSubClass', 'OverallCond', 
        'YrSold', 'MoSold','YearBuilt', "YearRemodAdd")
# process columns, apply LabelEncoder to categorical features
for c in cols:
    lbl = LabelEncoder() 
    lbl.fit(list(fulldata[c].values)) 
    fulldata[c] = lbl.transform(list(fulldata[c].values))

# shape        
print('Shape all_data: {}'.format(fulldata.shape))

int_features = fulldata.dtypes[fulldata.dtypes == "int64"].index
float_features = fulldata.dtypes[fulldata.dtypes == "float64"].index

# Check the skew of all numerical features
skewed_int_feats = fulldata[int_features].apply(lambda x: skew(x.dropna()))
skewed_float_feats = fulldata[float_features].apply(lambda x: skew(x.dropna()))

skewed_features = pd.concat([skewed_int_feats,skewed_float_feats])

print("\nSkewness in numerical features: \n")
skewness = pd.DataFrame({'Skew' :skewed_features})
skewness = skewness.sort_values('Skew', ascending = False)
skewness.head(15)


fulldata = pd.get_dummies(fulldata)
print(fulldata.shape)
fulldata["Functional"] = fulldata["Functional"].fillna("Typ")


sns.distplot(train['SalePrice'])
models = [['DecisionTree :',DecisionTreeRegressor()],
           ['RandomForest :',RandomForestRegressor()],
           ['KNeighbours :', KNeighborsRegressor(n_neighbors = 2)]]
from math import sqrt
print("Score")
for name,model in models:
    ModelTemp= make_pipeline(StandardScaler(),model)
    rmse=np.sqrt(-cross_val_score(model,x_train.values,y=y_train,scoring="neg_mean_squared_error",cv = 10))
    print("Average {} cross validation score: ".format(name), np.mean(rmse))


# In[ ]:




