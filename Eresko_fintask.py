#!/usr/bin/env python
# coding: utf-8

# ## K-Nearest Neighbors Analysis
# Use any financial ticker (except S&P500) to create the trading strategy, using KNN classifier.
# 
# **Task 6**. Upload data for one ticker (for the recent year) from Yahoo Finance. Make brief exploratory analysis of obtained data.
# 
# **Task 7**. Apply KNN classifier to obtained data. Assess the quality of the model. Create and briefly justify the trading strategy.

# In[29]:


# Data Manipulation
import numpy as np
import pandas as pd

# Plotting graphs
import matplotlib.pyplot as plt

# Machine learning libraries
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# Data fetching
get_ipython().system('pip install yfinance')
get_ipython().system('pip install pandas_datareader')
from pandas_datareader import data as pdr
import yfinance as yf

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# In[30]:


# Reading the data from Yahoo. I decided to take Spotify Technology S.A. data for my task. 
df= pdr.get_data_yahoo('SPOT', '2019-12-01', '2020-12-01')
df = df.dropna()
df = df[['Open', 'High', 'Low', 'Close']]
df.head()


# In[31]:


# Let's perform some exploratory analysis. First of all, let's just build a graph of close prices throughout the timeframe. 
df['Close'].plot()
plt.xlabel("Date")
plt.ylabel("Close price")
plt.title("Spotify Technology S.A.")
plt.style.use('seaborn-bright')
plt.show()


# In[32]:


# Let's add a Daily Lag variable to further calculate and add Daily Returns variable.
df['Daily Lag'] = df['Close'].shift(1)
df['Daily Returns'] = (df['Daily Lag']/df['Close']) -1
df.head()


# In[33]:


# Let's calculate kurtosis value for daily returns. According to Ivanovski, Zoran & Stojanovski, Toni & Narasanov, Zoran, 2015. 
# "Volatility And Kurtosis Of Daily Stock Returns At Mse," most of the investors are risk-averse which means
# that they prefer a distribution with low kurtosis. Our data has quite a low value of kurtosis at 1.97, which means Spotify 
# stocks are quite good for investment. (Kurtosis evaluation according to: 
# https://qoppac.blogspot.com/2019/11/kurtosis-and-expected-returns.html)

df['Daily Returns'].kurtosis()


# In[34]:


# Now let's move on to creating a trading strategy.
df= pdr.get_data_yahoo('SPOT', '2019-12-01', '2020-12-01')
df = df.dropna()
df = df[['Open', 'High', 'Low', 'Close']]
# Predictor variables for the data: Open-Close and High-Low.
df['Open-Close']= df.Open -df.Close
df['High-Low']  = df.High - df.Low
df =df.dropna()
X= df[['Open-Close', 'High-Low']]
X.head()


# In[35]:


# Defining a target variable: whether the price of our index will close up or down on the next day.
Y = np.where(df['Close'].shift(-1)>df['Close'],1,-1)


# In[36]:


# Splitting the dataset as train and sample sets. Train dataset will be 60% as it is an advised number for good measurements.
split_percentage = 0.6
split = int(split_percentage*len(df))

X_train = X[:split]
Y_train = Y[:split]

X_test = X[split:]
Y_test = Y[split:]


# In[37]:


# Instantiate KNN learning model(k=16)
# I played around with k value a bit and decided to stick with k=16 as it had quite good results with numbers > 0.50. 
knn = KNeighborsClassifier(n_neighbors=16)

# fit the model
knn.fit(X_train, Y_train)

# Accuracy Score
accuracy_train = accuracy_score(Y_train, knn.predict(X_train))
accuracy_test = accuracy_score(Y_test, knn.predict(X_test))

print ('Train_data Accuracy: %.2f' %accuracy_train)
print ('Test_data Accuracy: %.2f' %accuracy_test)


# In[38]:


# Predicted Signal
df['Predicted_Signal'] = knn.predict(X)

# Spotify Technology S.A. Cumulative Returns
df['spot_returns'] = np.log(df['Close']/df['Close'].shift(1))
Cumulative_spot_returns = df[split:]['spot_returns'].cumsum()*100

# Cumulative Strategy Returns 
df['Startegy_returns'] = df['spot_returns']* df['Predicted_Signal'].shift(1)
Cumulative_Strategy_returns = df[split:]['Startegy_returns'].cumsum()*100

# Plot the results to visualize the performance

plt.figure(figsize=(20,5))
plt.plot(Cumulative_spot_returns, color='r',label = 'SPOT Returns')
plt.plot(Cumulative_Strategy_returns, color='g', label = 'Strategy Returns')
plt.legend()
plt.show()
# Here we can see that the strategy generally follows the same pattern despite being just a bit ahead of real returns in trends.
# The cumulative returns for SPOT seem to be the same as our strategy predicts. 


# In[39]:


# Calculate Sharpe ratio
# Sharpe ratio helps us understand whether the risk-adjusted return for the investment is attractive or not.
# We have a positive value here of 2.19, so investing in Spotify stocks according to our strategy would bring us some cash,
# however, it is recommended to create and diversify an investment portfolio as opposed to investing into one company.
# This is a whole different story, though. For now, it is a pretty safe investment for a beginner.
Std = Cumulative_Strategy_returns.std()
Sharpe = (Cumulative_Strategy_returns-Cumulative_spot_returns)/Std
Sharpe = Sharpe.mean()
print('Sharpe ratio: %.2f'%Sharpe)

