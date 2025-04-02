from app.utils.data_processing import Raman_Spectra
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, mock_open
import os

# Mock the Raman_Spectra class
@pytest.fixture
def raman_spectra_instance():
    return Raman_Spectra('/mock/path', 'mock_name')

# Test the __str__ method
def test_str_method(raman_spectra_instance):
    assert str(raman_spectra_instance) == "handeling sample : mock_name"

# Test the read_folder method
@patch('os.listdir')
@patch('pandas.read_csv')
def test_read_folder(mock_read_csv, mock_listdir, raman_spectra_instance):
    mock_listdir.return_value = ['file1.csv', 'file2.csv']
    mock_read_csv.return_value = pd.DataFrame({'wavenumber': [1, 2, 3], 'signal': [4, 5, 6]})
    all_data = raman_spectra_instance.read_folder()
    assert not all_data.empty
    assert all_data.shape == (3, 2)
    
    
def test_order_data(raman_spectra_instance):
    # Mock the all_data attribute
    raman_spectra_instance.all_data = pd.DataFrame({
        'wavenumber': [1, 2, 3, 2650, 2750, 1550, 1650],
        'signal1': [4, 5, 6, 7, 8, 9, 10],
        'signal2': [10, 9, 8, 7, 6, 5, 4]
    })
    sorted_data = raman_spectra_instance.Order_data()
    assert sorted_data.shape == raman_spectra_instance.all_data.shape
    assert sorted_data.shape == raman_spectra_instance.show_sorted().shape

