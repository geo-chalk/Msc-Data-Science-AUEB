# Import libraries needed for this part to be independent of the other parts
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

import seaborn as sns

import time
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

import tensorflow as tf
import tensorflow_docs as tfdocs
import tensorflow_docs.modeling
import tensorflow_docs.plots

from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten, BatchNormalization, Dropout
from keras.regularizers import l2

from xgboost import XGBRegressor
import catboost as cb
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor

import warnings
warnings.filterwarnings("ignore")



def plot_model_var_imp(model, X):
    """
    Plot the feature importances of a fiven model (only for models that feature importance is supported)
    INPUT: Model, predictors
    OUTPUT: None
    """
    # Print feature importancies
    predictors = [x for x in X.columns]
    feat_imp = pd.DataFrame(model.feature_importances_, predictors, columns = ['Feature Importance']).sort_values(by=['Feature Importance'], ascending=False)
    fig = feat_imp.plot(kind='bar', title='Feature Importances', figsize=(20,8))
    fig.axes.title.set_size(20)
    _ = plt.ylabel('Feature Importance Score')


def compare_predictions(pred_1, pred_2):
    """
    Plot a histogran of the actual vs predicted values. 
    INPUT: pred_1 - True Values, pred_2 - predicted values
    OUTPUT: None
    """
    bins = np.histogram(np.hstack((pred_1, pred_2)), bins=100)[1] #get the bin edges
    plt.hist(pred_1, bins=bins, alpha=1)
    plt.hist(pred_2, bins=bins, alpha=0.7)
    plt.title("Actual vs Predictions")
    plt.xlabel("Valence")
    plt.ylabel("Number of instances")
    plt.legend(["Actual", "Predictions"])
    plt.show()


def run_NN(X_train, X_test, y_train, y_test):

    st = time.time()
    STEPS_PER_EPOCH = 20
    lr_schedule = tf.keras.optimizers.schedules.InverseTimeDecay(
            0.001,
            decay_steps=STEPS_PER_EPOCH*1000,
            decay_rate=1,
            staircase=False)
            
    CALLBACKS = [
        tfdocs.modeling.EpochDots(),
        tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=10),
    ]
    optimizer = tf.keras.optimizers.Adam(lr_schedule)
    NN_model = Sequential()
    NN_model.add(Dense(128, kernel_initializer='normal', input_dim=X_train.shape[1], activation='elu'))
    NN_model.add(Dropout(0.5))
    NN_model.add(Dense(512, activation='elu', activity_regularizer=l2(0.0001)))
    NN_model.add(Dropout(0.5))
    NN_model.add(Dense(256, activation='elu', activity_regularizer=l2(0.0001)))
    NN_model.add(Dropout(0.5))
    NN_model.add(Dense(32, activation='elu', activity_regularizer=l2(0.0001)))
    NN_model.add(Dropout(0.5))
    NN_model.add(Dense(1, kernel_initializer='normal', activation='linear'))
    NN_model.compile(loss='mae', optimizer=optimizer)
    history = NN_model.fit(X_train, y_train, epochs=500, batch_size=256, verbose=2, validation_split=0.2, callbacks=CALLBACKS)

    plt.figure(figsize=(15,10))
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train', 'validation'], loc='upper left')
    plt.show()

    pred_nn = NN_model.predict(X_test)
    print('Neural Network MAE with {0} training data points:'.format(len(X_train)),
            str(np.sqrt(mean_absolute_error(pred_nn, y_test))))
    print('Neural Network CPU Time:', time.time() - st, 'seconds\n')

    return NN_model    



def pre_processing(df_raw, reduced=False, dummy=False):
    """
    Function to perform re-processing of the the input Dataframes
    INPUT: raw data
    OUTPUT: processed Data
    OPTIONS: 
        reduced: exclude the extra features for faster training
        dummy: one-hot encode categorical data  
    """
    # We don't need the id columns, and the uri/l columns so we will drop those:
    col_to_drop = ['song_id', 'id', 'track_href', 'analysis_url', 'type', 'uri']
    df_raw.drop(col_to_drop, axis=1, inplace=True)
    df_raw.head()

    #  Move dependent variable to the end to make if more pythonic
    order = ['danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 
            'liveness', 'tempo', 'tempo_confidence', 'duration_ms', 'time_signature_confidence', 
            'key_confidence', 'mode_confidence', 'max_loundness', 'min_loundness', 'mode_seg_0', 'fade_in', 'fade_out',
        'pitch_0', 'pitch_1', 'pitch_2', 'pitch_3', 'pitch_4', 'pitch_5',
        'pitch_6', 'pitch_7', 'pitch_8', 'pitch_9', 'pitch_10', 'pitch_11',
        'timbre_0', 'timbre_1', 'timbre_2', 'timbre_3', 'timbre_4', 'timbre_5',
        'timbre_6', 'timbre_7', 'timbre_8', 'timbre_9', 'timbre_10',
        'timbre_11', 'key', 'mode', 'time_signature', 'valence']
    df_raw = df_raw[order]

    # drop uneeded columns 
    if reduced:
        not_needed = ['tempo_confidence', 'time_signature_confidence', 
                'key_confidence', 'mode_confidence', 'max_loundness', 'min_loundness', 'mode_seg_0', 'fade_in', 'fade_out',
            'pitch_0', 'pitch_1', 'pitch_2', 'pitch_3', 'pitch_4', 'pitch_5',
            'pitch_6', 'pitch_7', 'pitch_8', 'pitch_9', 'pitch_10', 'pitch_11',
            'timbre_0', 'timbre_1', 'timbre_2', 'timbre_3', 'timbre_4', 'timbre_5',
            'timbre_6', 'timbre_7', 'timbre_8', 'timbre_9', 'timbre_10',
            'timbre_11']
        df_raw.drop(not_needed, axis=1, inplace = True)

    #One hot encode variables
    if dummy:
        df_raw = pd.get_dummies(df_raw, columns=['key', 'mode', 'time_signature'])

    order = list(df_raw.columns)
    order.remove('valence')
    order.append('valence')

    df_raw = df_raw[order]


    return df_raw


def normalize(df_not_norm):
    """"
    INPUT: raw data
    OUTPUT: z-score normalized data
    """
    tim = [i for i in df_not_norm.columns if  'timbre' in i]
    col_to_norm = ['loudness', 'tempo', 'duration_ms', 'max_loundness', 'min_loundness', 'fade_in', 'fade_out'] + tim
    # Scale/normalize numeric columns by calculating the z-score of each value.
    scaler = StandardScaler(copy = True)
    df_not_norm[col_to_norm] = scaler.fit_transform(df_not_norm[col_to_norm].to_numpy())
    return df_not_norm    


def correlation_table_s2(df):
    """"
    function to plot correlation table
    """
    colormap = plt.cm.viridis
    plt.figure(figsize=(10,7))
    plt.title('Pearson Correlation of Features', y=1.05, size=15)
    sns.heatmap(df.corr().round(2)\
                ,linewidths=0.1,vmax=1.0, square=True, cmap=colormap, \
                linecolor='white', annot=True)


def evaluate(results):
    """
    Visualization code to display results of various learners.
    
    inputs:
      - learners: a list of supervised learners
      - stats: a list of dictionaries of the statistic results from 'train_predict()'

    """
  
    # Create figure
    fig, ax = plt.subplots(2, 3, figsize = (20,10))

    # Constants
    bar_width = 0.3
    colors = ['#A00000','#00A0A0','#00A000']
    
    # Super loop to plot four panels of data
    for k, learner in enumerate(results.keys()):
        for j, metric in enumerate(['train_time', 'cross_val_mae_train', 'cross_val_RMSE_train', 'pred_time', 'mae_test','RMSE_test']):
            for i in np.arange(3):
                
                # Creative plot code
                ax[j//3, j%3].bar(i+k*bar_width, results[learner][i][metric], width = bar_width, color = colors[k])
                ax[j//3, j%3].set_xticks([0.45, 1.45, 2.45])
                ax[j//3, j%3].set_xticklabels(["20%", "40%", "100%"])
                ax[j//3, j%3].set_xlabel("Training Set Size")
                ax[j//3, j%3].set_xlim((-0.1, 3.0))
    
    # Add unique y-labels
    ax[0, 0].set_ylabel("Time (in seconds)")
    ax[0, 1].set_ylabel("Score")
    ax[0, 2].set_ylabel("Cross Validation Score")
    ax[1, 0].set_ylabel("Time (in seconds)")
    ax[1, 1].set_ylabel("Score")
    ax[1, 2].set_ylabel("Cross Validation Score")
    
    # # Add titles
    ax[0, 0].set_xlabel("Model Training")
    ax[0, 1].set_xlabel("Cross Validation Score (MAE) on Training Subset")
    ax[0, 2].set_xlabel("Cross Validation Score (RMSE) on Training Subset")
    ax[1, 0].set_xlabel("Model Predicting")
    ax[1, 1].set_xlabel("MAE Score on Test Set")
    ax[1, 2].set_xlabel("RMSE Score on Test Set")
    
    # Set y-limits for score panels
    ax[0, 1].set_ylim((0, 0.2))
    ax[0, 2].set_ylim((0, 0.2))
    ax[1, 1].set_ylim((0, 0.2))
    ax[1, 2].set_ylim((0, 0.2))

    # Create patches for the legend
    patches = []
    for i, learner in enumerate(results.keys()):
        patches.append(mpatches.Patch(color = colors[i], label = learner))
    plt.legend(handles = patches, \
               loc = 'upper left',bbox_to_anchor=(0.6, 0.0, 0.0, 2.5))
    
    # Aesthetics
    plt.suptitle("Performance Metrics for Top Models", fontsize = 26, y = 1)
    # plt.tight_layout()
    plt.show()
    

def train_predict(learner, sample_size, X_train, y_train, X_test, y_test): 
    '''
    inputs:
        - learner: the learning algorithm to be trained and predicted on
        - sample_size: the size of samples (number) to be drawn from training set
        - X_train: features training set
        - y_train: dependent var training set
        - X_test: features testing set
        - y_test: dependent var testing set
    '''

    results = {}

    # Fit the learner to the training data 
    start = time.time() # Get start time
    learner = learner.fit(X_train[:sample_size], y_train[:sample_size])
    end = time.time() # Get end time

    results['train_time'] = end - start
        
    # Get the predictions on the test set(X_test),
    # then get predictions on the first 3000 training samples(X_train) using .predict()
    start =  time.time() # Get start time
    predictions_test = learner.predict(X_test)
    end =  time.time() # Get end time

    # Calculate the total prediction time
    results['pred_time'] = end - start
            
    if learner.__class__.__name__ == 'CatBoostRegressor':
        cv = 3
    else:
        cv = 10
    # Compute accuracy on the first 3000 training samples 
    results['cross_val_mae_train'] = -cross_val_score(learner, X_train[:3000], y_train[:3000], cv=cv, 
                            scoring="neg_mean_absolute_error").mean()
        
    # Compute accuracy on test 
    results['mae_test'] = mean_absolute_error(predictions_test, y_test)

    # Compute RMSE on the the first 3000 training samples 
    results['cross_val_RMSE_train'] = -cross_val_score(learner, X_train[:3000], y_train[:3000], cv=cv, 
                            scoring="neg_root_mean_squared_error").mean()
        
    # Compute RMSE on the test set 
    results['RMSE_test'] = np.sqrt(mean_squared_error(predictions_test, y_test))

    # Success
    print("{} trained on {} samples.".format(learner.__class__.__name__, sample_size))
        
    # Return the results
    return results                