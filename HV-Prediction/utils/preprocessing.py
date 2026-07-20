"""
preprocessing.py

This module provides utility functions for feature selection and transformation
in data analysis and machine learning. It includes functions for selecting features
based on correlation, variance, entropy calculations, and normalization of features.

Author: 
Date: Dec 2 2024
Version: 1.1

Date: Jul 18 2025
Version: 2.1

Date: Aug 23 2025
Version 2.2
"""

import pandas as pd
import numpy as np

# Functions
def select_element_features(elem_list: list, phys_param: pd.DataFrame, sel_key: str):
    """
    Select features by element as columns in ``pandas.DataFrame``.

    Parameters:
        elem_list (list): List of elements to select.
        phys_param (pd.DataFrame): DataFrame containing physical parameters.
        sel_key (str): Column name to match elements.

    Returns:
        np.ndarray: Indices of the selected elements.
    """
    idx = []
    for elem in elem_list:
        idx.append(phys_param[phys_param[sel_key] == elem].index.values)
    
    idx = np.array(idx).flatten()
    return idx

def calculate_D(C, x):
    """
    Calculate the D matrix based on input matrices C and x.

    Parameters:
        C (np.ndarray): Matrix of coefficients.
        x (np.ndarray): Input data matrix.

    Returns:
        np.ndarray: Output matrix D.
    """
    C = np.array(C)
    x = np.array(x)

    # Ensure C and x have matching dimensions
    if C.shape[1] != x.shape[0]:
        raise ValueError("The number of columns in C must match the number of rows in x.")

    # Create output array with shape (C.shape[0], x.shape[1])
    D_output = np.zeros((C.shape[0], x.shape[1]))

    # Iterate over each row of C
    for idx in range(C.shape[0]):
        # Iterate over each column j of x
        for j in range(x.shape[1]):
            d = 0.0  # Initialize D to 0
            # Calculate D for the current column j
            for i in range(C.shape[1]):  # C's column count
                for k in range(C.shape[1]):  # Calculate absolute difference
                    if i != k:
                        d += C[idx][i] * C[idx][k] * abs(x[i][j] - x[k][j])
            D_output[idx][j] = d  # Store result

    return D_output

def entropy(comp: pd.DataFrame):
    """
    Calculate the entropy for each composition.

    Parameters:
        comp (pd.DataFrame): DataFrame containing composition data.

    Returns:
        np.ndarray: Array of entropy values for each composition.
    """
    ens = []
    for i in range(comp.shape[0]):
        en = 0
        for c in comp.values[i]:
            if c != 0:
                en += np.log(c) * c
        ens.append(abs(en))
    
    return np.array(ens)

def calculate_H_mix(comp:pd.DataFrame, H:np.ndarray):
    """
    Calculate the enthalpy of mixing for each composition.

    Parameters:
        comp (pd.DataFrame): DataFrame containing composition data.
        comp.shape = (m,n) m compositions n components
        H (np.ndarray): binary mixing enthalpy.
        H.shape = (n,n)

    Returns:
        np.ndarray: Array of enthalpy values for each composition.
    """
    c = comp.values
    H_mix = []
    for ci in c:
        outer = np.outer(ci, ci)
        total = 4 * np.sum(outer * H)
        diag_sum = 4 * np.sum(ci**2 * np.diag(H))
        H_mix.append((total - diag_sum)/2)
        
    return np.array(H_mix)

def generate_features(comp, phys, elem_namelist, phys_namelist):
    """
    Generate composition-related physical features.

    Parameters:
        comp (array-like): Composition data.
        phys (array-like): Physical property data.
        elem_namelist (list): List of element names.
        phys_namelist (list): List of physical property names.

    Returns:
        pandas.DataFrame: DataFrame containing the generated features.
    """
    mean_feature = np.dot(comp, phys)
    var_feature = np.zeros_like(mean_feature)
    f_feature = np.zeros_like(mean_feature)

    for i in range(mean_feature.shape[0]):
        for j in range(mean_feature.shape[1]):
            tmp = np.square(1 - (phys[:, j] / mean_feature[i, j]))
            # var_feature[i][j] = np.average(tmp, weights=comp[i]) 
            # Update at March 4 2025 V: sqaure root variance
            var_feature[i][j] = np.sqrt(np.average(tmp, weights=comp[i]))
            f_feature[i][j] = np.max(comp * tmp) - np.min(comp * tmp)
    
    d_feature = calculate_D(comp, phys)

    # Construct feature names
    mean_namelst = ['M' + name for name in phys_namelist]
    var_namelst = ['V' + name for name in phys_namelist]
    f_namelst = ['F' + name for name in phys_namelist]
    d_namelst = ['D' + name for name in phys_namelist]

    # Combine all features into a single DataFrame
    feature_data = np.hstack((comp, mean_feature, var_feature, f_feature, d_feature))
    feature_columns = elem_namelist + mean_namelst + var_namelst + f_namelst + d_namelst

    feature = pd.DataFrame(feature_data, columns=feature_columns)
    return feature


def normalize_features(ref_data,norm_data,scaler):
    """
    Normalize features of the input DataFrame using Min-Max scaling.

    Parameters:
        data (pd.DataFrame): The input DataFrame containing the features to be normalized.

    Returns:
        pd.DataFrame: A DataFrame containing the normalized features.
    """

    # Get the original column names from the input DataFrame
    data_lst = ref_data.columns.tolist()
    
    # Fit the scaler to the data and transform it
    data_norm = scaler.fit(ref_data).transform(norm_data)
    
    # Convert the normalized data back into a DataFrame with the original column names
    data_norm = pd.DataFrame(data_norm, columns=data_lst)
    
    return data_norm

# Added in Jul 2025 (Ver 2.1)
def remove_duplicates(lst):
    """Remove duplicate items from a list while preserving order.

    Args:
        lst (list): Input list with possible duplicates.

    Returns:
        list: List with duplicates removed.
    """
    unique_list = []
    [unique_list.append(item) for item in lst if item not in unique_list]
    return unique_list