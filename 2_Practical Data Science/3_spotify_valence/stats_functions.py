import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns


# Show correlation table
def correlation_table(df):
    colormap = plt.cm.viridis
    plt.figure(figsize=(10,7))
    plt.title('Pearson Correlation of Features', y=1.05, size=15)
    sns.heatmap(df.corr().round(2)\
                ,linewidths=0.1,vmax=1.0, square=True, cmap=colormap, \
                linecolor='white', annot=True)

def plot_model_selection(models, best_model, reverse=False):
    """
    Function that plots the adjusted r-squared based on the number of parameters, 
    also indicating the position of the best found R-squared.
    """
    if reverse:
        models = models[::-1]
    all_rsquared = np.array([ x.rsquared  for x in models ])
    all_rsquared_adj = np.array([ x.rsquared_adj  for x in models ])
    best_indx =len(best_model.model.exog_names)
    print(best_indx)
    x = np.arange(1, len(all_rsquared)+1)

    plt.figure(figsize=(8, 6))
    plt.plot(x, all_rsquared, marker='*', label='$R^2$')
    plt.plot(x, all_rsquared_adj, marker='o', label='Adjusted $R^2$')
    plt.plot(best_indx, all_rsquared_adj[best_indx], marker='x', markersize=14, color='k')
    plt.legend()
    plt.title('$R^2$ vs Adjusted $R^2$', fontsize=20)

def process_subset(y, data, feature_set):
    """
    Function that takes the subset of a model and returns the fitted regression model
    INPUT: dependent variable, the dataframe to process
    """
    X = data.loc[:, feature_set].values
    X = sm.add_constant(X)
    names = ['intercept']
    names.extend(feature_set)
    model = sm.OLS(y, X)
    model.data.xnames = names
    regr = model.fit()
    return regr         

def forward_add_variable(data, exog, selected, to_select):
    best_rsquared = 0
    best_model = None
    best_column = None
    y = data.loc[:, exog]
    
    for column in to_select:
        new_selected = selected + [column]
        regr = process_subset(y, data, new_selected)
        if regr.rsquared > best_rsquared:
            best_rsquared = regr.rsquared
            best_model = regr
            best_column = column
    
    return best_model, best_column

def forward_stepwise_selection(data, exog, printing=False):

    best_models = []
    best_model = None
    selected = []
    to_select = [ x for x in data.columns if x != exog ] 

    p = len(to_select) + 1

    for i in range(1, p):
        if printing:
            print(f'Finding the best model for {i} variable{"s" if i > 1 else ""}')
        model, best_column = forward_add_variable(data, exog, selected, to_select)
        selected.append(best_column)
        to_select.remove(best_column)
        if not best_model or model.rsquared_adj > best_model.rsquared_adj:
            best_model = model
        if printing:
            print(selected)
        best_models.append(model)
        
    print(f'Fitted {1 + p*(p+1)//2} models')
    return best_model, best_models

def backward_remove_variable(data, exog, selected):
    
    best_rsquared = 0
    best_model = None
    best_column = None
    y = data.loc[:, exog]
    
    for column in selected:
        new_selected = selected[:]
        new_selected.remove(column)
        regr = process_subset(y, data, new_selected)
        if regr.rsquared > best_rsquared:
            best_rsquared = regr.rsquared
            best_model = regr
            best_column = column
    
    return best_model, best_column

def backward_stepwise_selection(data, exog, printing=False):

    best_models = []
    selected = [ x for x in data.columns if x != exog ]

    p = len(selected) + 1
    if printing:
        print(f'Finding the best model for {p - 1} variables')
        print(selected)
    y = data.loc[:, exog]
    best_model = process_subset(y, data, selected)
    best_models.append(best_model)

    for i in reversed(range(2, p)):
        if printing:
            print(f'Finding the best model for {i - 1} variable{"s" if (i - 1) > 1 else ""}')
        model, best_column = backward_remove_variable(data, exog, selected)
        selected.remove(best_column)
        if not best_model or model.rsquared_adj > best_model.rsquared_adj:
            best_model = model
        if printing:
            print(selected)
        best_models.append(model)
        
    print(f'Fitted {1 + p*(p+1)//2} models')
    return best_model, best_models        

def plot_model_AIC(models, best_model, reverse=False):
    """
    Function that plots the adjusted r-squared based on the number of parameters, 
    also indicating the position of the best found R-squared.
    """
    if reverse:
        models = models[::-1]
    aic = np.array([ x.aic for x in models ])
    bic = np.array([ x.bic for x in models ])
    all_rsquared_adj = np.array([ x.rsquared_adj  for x in models ])
    best_indx =len(best_model.model.exog_names)
    print(best_indx)
    x = np.arange(1, len(aic)+1)


    fig, ax1 = plt.subplots(figsize=(8, 6))
    ax2 = ax1.twinx()

    ax1.plot(x, aic, marker='*', label='AIC', color = 'red')
    ax1.plot(x, bic, marker='*', label='BIC', color = 'green')
    ax2.plot(x, all_rsquared_adj, marker='o', label='Adjusted $R^2$')
    ax2.plot(best_indx, all_rsquared_adj[best_indx], marker='x', markersize=14, color='k')
    fig.legend(loc='center right',bbox_to_anchor=(0.4, 0.2, 0.47, 0.5))
    plt.title('AIC/BIC vs Adjusted $R^2$', fontsize=20)    