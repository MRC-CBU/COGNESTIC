import mne
from mne.decoding import Scaler
from mne.cov import compute_covariance, compute_whitener
from mne.io.pick import _picks_to_idx as picks_to_idx

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, FunctionTransformer

from scipy.stats import pearsonr
import numpy as np


def whiten_epochs(
    epochs,
    cov_cond_query,
    data_cond_query,
    picks=['mag', 'grad', 'eeg']
):
    """Whiten epochs
    
    Parameters
    ----------
    epochs : mne.Epochs
        Epochs object
    Returns
    -------
    data : numpy.array, shape (n_trials, n_sensors, n_time)
        Data array
    """
    
    # Compute covariance matrix based on the baseline of the written epochs
    noise_cov = compute_covariance(
        epochs[cov_cond_query],
        tmin=None,
        tmax=0,
        method='ledoit_wolf',
        n_jobs=None,
        projs=None,
        rank='info'
    )
    # Compute whitener, choosing the best covariance estimator
    W, _ = compute_whitener(noise_cov,
                            epochs.info,
                            picks=picks_to_idx(epochs.info, picks),
                            pca=True
    )
    # Get epochs data
    data = epochs[data_cond_query].get_data(picks=picks_to_idx(epochs.info, picks))
    # Apply whitener to data
    data = (np.dot(data.swapaxes(1, 2), W.T)).swapaxes(1, 2)

    return data


def windowizer(
    X,
    window_size=10,
    win_func='expand_features'
):
    """Windowizer function to create a sliding window of size window_size
    over the last dimension of the input data X.
    
    Parameters
    ----------
    X : np.ndarray
        Input data of shape (n_examples, n_features, n_timepoints)
    window_size : int
        Size of the sliding window in timepoints.
    win_func : str
        Function to apply to the windowed data. Options are 'expand_features' or 'mean'.
        - 'expand_features' reshapes the data within each window to yield a 
            n_features*window_size array. This is performed in a moving window 
            fashion for each timepoint (so that there is window_size-1) overlap 
            between windows. This is computed separately for each example, so 
            the output shape is 
            (n_examples, n_features*window_size, n_timepoints-window_size+1)
        - 'mean'computes the moving average of the data across the timepoints 
            separately for each example. The output shape is 
            (n_examples, n_features, n_timepoints-window_size)
    """

    assert win_func in ['expand_features', 'mean']
    
    X_win = []
    for i in range(0, X.shape[-1]-window_size+1):
        temp = X[:, :, i:i+window_size]
        if win_func == 'expand_features':
            temp = np.reshape(temp, (temp.shape[0], -1))
        elif win_func == 'mean':
            temp = np.mean(temp, axis=-1)
        X_win.append(np.expand_dims(temp, axis=-1))
    X_win = np.concatenate(X_win, axis=-1)

    return X_win


def pseudotrial_generator(
    X,
    y,
    n_trials_to_average=8
):
    """Function to average the examples of each condition in X and y into
    evoked responses based on the number of examples to average.
    
    Parameters
    ----------
        X : np.ndarray
            Input data of shape (n_examples, n_features, n_timepoints)
        y : np.ndarray
            Labels of the input data of shape (n_examples)
        n_trials_to_average : int
            Number of examples to average from the same condition to create the 
            evoked response.
    Returns
    -------
        X_avg : np.ndarray
            Averaged data of shape (n_evoked, n_features, n_timepoints)
        y_avg : np.ndarray
            Labels of the averaged data of shape (n_evoked)
    """
    labels, label_ind = np.unique(y, return_inverse=True)
    X_avg = []
    y_avg = []
    # Loop around conditions (labels)
    for i in range(len(labels)):
        # select indices of the current condition and shuffle them
        temp = np.squeeze(np.argwhere(label_ind == i))
        np.random.shuffle(temp)
        # compute the number of examples after averaging given the number of examples to average
        n_avg_examples = int(np.ceil(len(temp)/n_trials_to_average))
        # select the indices of the examples to average
        # create index for averaging based on the modulo of the number of averaged examples
        temp_ind = np.array([j%n_avg_examples for j in range(0, len(temp))])
        avg_ind = [temp[np.squeeze(np.argwhere(temp_ind == j))] for j in range(n_avg_examples)]
        # Average the examples based on the computed indices
        for ind in avg_ind:
            X_avg.append(np.mean(X[ind], axis=0, keepdims=True))
            y_avg.append(labels[i])
    X_avg = np.concatenate(X_avg, axis=0)
    y_avg = np.array(y_avg)
    return X_avg, y_avg


def over_sample(
    X,
    y,
    factor=10
):
    """Function to over-sample the data by a factor
    Details
    -------
        - The function over-samples the data by randomly selecting examples 
          from each condition with replacement
    Parameters
    ----------
        X : np.ndarray
            Input data of shape (n_examples, n_features, n_timepoints)
        y : np.ndarray
            Labels of the input data of shape (n_examples)
        factor : int
            Factor to over-sample the data by
    Returns
    -------
        X_over : np.ndarray
            Over-sampled data of shape (n_examples*factor, n_features, n_timepoints)
        y_over : np.ndarray
            Labels of the over-sampled data of shape (n_examples*factor)
    """
    X_over = []
    y_over = []
    for ui in np.unique(y):
        temp = np.squeeze(np.argwhere(y == ui))
        temp = np.random.choice(temp, size=factor*len(temp))
        X_over.append(X[temp])
        y_over.append(y[temp])
    X_over = np.concatenate(X_over, axis=0)
    y_over = np.concatenate(y_over, axis=0)
    return X_over, y_over


def pearsonr_score(y, y_pred):
    """Custom score function based on the Pearson correlation coefficient"""
    return pearsonr(y, y_pred)[0]


def moving_window_preprocessor(
    moving_window_size=10,
    moving_window_func='expand_features'
):
    # Create a pipeline with a scaler and a windowizer. The latter makes it 
    # possible to run mvpa on a sliding window of the data, instead of single 
    # timepoints. 
    preprocessor = Pipeline(
        [('scaler', Scaler(scalings='mean')),
        ('windowizer', FunctionTransformer(
            windowizer,
            kw_args={'window_size': moving_window_size, 'win_func': moving_window_func}))]
    )
    return preprocessor