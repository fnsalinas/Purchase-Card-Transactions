import os
import pandas as pd
import pytest
from src.data.cleaner import clean_data

def test_clean_data_handles_missing_input(caplog):
    """
    Test that clean_data handles a missing file gracefully.
    """
    clean_data('data/non_existent.csv', 'data/output.csv')
    assert "Input file data/non_existent.csv not found." in caplog.text

def test_clean_data_basic(tmp_path):
    """
    Test the basic functionality of clean_data on a mock dataframe.
    """
    input_file = tmp_path / "raw_consolidated.csv"
    output_file = tmp_path / "prepared_consolidated.csv"
    
    mock_data = pd.DataFrame({
        "file_name": ["test.xls", "test.xls"],
        "sheet_name": ["Sheet1", "Sheet1"],
        "trans_date": ["2020-01-01", None],  # One invalid date to be dropped
        "unnamed": ["Dir A", "Dir B"],
        "directorate": [None, "Dir B"],
        "merchant_name": ["amazon UK", "TESCO local"],
        "trans_cac_code_1": ["A1", None],
        "trans_cac_code_2": ["B1", "B2"],
        "trans_cac_desc_1": ["Desc 1", None],
        "trans_cac_desc_2": ["Desc B1", "Desc B2"]
    })
    
    mock_data.to_csv(input_file, sep='~', index=False)
    
    clean_data(str(input_file), str(output_file))
    
    assert os.path.exists(output_file)
    result_df = pd.read_csv(output_file, sep='~')
    
    # One row should have been dropped due to null trans_date
    assert len(result_df) == 1
    
    # Directorate should be completed from 'unnamed'
    assert result_df.iloc[0]['directorate'] == "Dir A"
    
    # Merchant name should be standardized
    assert result_df.iloc[0]['merchant_name'] == "Amazon"
