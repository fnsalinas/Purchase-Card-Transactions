import glob
import logging
import os
import pandas as pd
import pandera as pa

logger = logging.getLogger(__name__)

# Basic schema to ensure the consolidated dataframe has the expected structure
# and types before proceeding to the cleaning phase.
consolidated_schema = pa.DataFrameSchema({
    "file_name": pa.Column(str, nullable=False),
    "sheet_name": pa.Column(str, nullable=False),
    # Some types might be mixed (e.g. floats as strings) due to dirty raw data,
    # so we are lenient in the initial validation, focusing on existence.
    "trans_date": pa.Column(nullable=True),
    "trans_vat_desc": pa.Column(nullable=True),
    "original_gross_amt": pa.Column(nullable=True),
    "original_cur": pa.Column(nullable=True),
    "merchant_name": pa.Column(nullable=True),
    "card_number": pa.Column(nullable=True),
    "billing_gross_amt": pa.Column(nullable=True),
    "billing_cur_code": pa.Column(nullable=True),
    "billing_cur_code_1": pa.Column(nullable=True),
    "trans_tax_amt": pa.Column(nullable=True),
    "trans_cac_code_1": pa.Column(nullable=True),
    "trans_cac_desc_1": pa.Column(nullable=True),
    "trans_cac_code_2": pa.Column(nullable=True),
    "trans_cac_desc_2": pa.Column(nullable=True),
    "trans_cac_code_3": pa.Column(nullable=True),
    "directorate": pa.Column(nullable=True),
    "unnamed": pa.Column(nullable=True)
}, strict=False)

def consolidate_data(input_dir='data/raw', output_path='data/interim/raw_consolidated_data.csv'):
    """
    Reads all raw Excel and CSV files, renames columns to a standard format,
    consolidates them into a single dataframe, and saves to interim data.
    """
    logger.info(f"Consolidating data from {input_dir}")
    
    xls_files = glob.glob(os.path.join(input_dir, '*.xls'))
    # csv_files = glob.glob(os.path.join(input_dir, '*.csv'))
    
    df_list = []
    
    for file in xls_files:
        logger.debug(f'Reading {file}')
        try:
            df_sheets = pd.read_excel(file, sheet_name=None)
            for sheet in df_sheets.keys():
                df_sheet = df_sheets[sheet]
                df_sheet['file_name'] = os.path.basename(file)
                df_sheet['sheet_name'] = sheet
                if df_sheet.shape[0] > 0:
                    df_list.append(df_sheet)
        except Exception as e:
            logger.error(f"Error reading {file}: {e}")

    logger.info(f'Dataframes count after read: {len(df_list)}')
    
    # Removing unwanted sheets based on original logic
    df_list = [x for x in df_list if x.loc[0, 'sheet_name'] != 'Sheet2' if not x.empty]
    
    vars_rename = {
        'file_name': 'file_name',
        'sheet_name': 'sheet_name',
        'TRANS DATE': 'trans_date',
        'TRANS VAT DESC': 'trans_vat_desc',
        'ORIGINAL GROSS AMT': 'original_gross_amt',
        'ORIGINAL CUR': 'original_cur',
        'MERCHANT NAME': 'merchant_name',
        'CARD NUMBER': 'card_number',
        'BILLING GROSS AMT': 'billing_gross_amt',
        'BILLING CUR CODE': 'billing_cur_code',
        'BILLING CUR CODE.1': 'billing_cur_code_1',
        'TRANS TAX AMT': 'trans_tax_amt',
        'TRANS CAC CODE 1': 'trans_cac_code_1',
        'TRANS CAC DESC 1': 'trans_cac_desc_1',
        'TRANS CAC CODE 2': 'trans_cac_code_2',
        'TRANS CAC DESC 2': 'trans_cac_desc_2',
        'TRANS CAC CODE 3': 'trans_cac_code_3',
        'Directorate ': 'directorate',
        'Directorate': 'directorate',
        'Directorates': 'directorate',
        'Unnamed: 10': 'unnamed'
    }
    
    df_list = [x.rename(columns=vars_rename) for x in df_list]
    
    if not df_list:
        logger.warning("No data found to consolidate.")
        return
    
    df_concat = pd.concat(df_list, axis=0, ignore_index=True)
    
    cols = list(dict.fromkeys(list(vars_rename.values())))
    
    # Only keep the defined columns
    existing_cols = [c for c in cols if c in df_concat.columns]
    df_concat = df_concat[existing_cols].copy()
    
    # Add missing columns with None to match schema
    for c in cols:
        if c not in df_concat.columns:
            df_concat[c] = None

    # Validate schema
    try:
        consolidated_schema.validate(df_concat)
        logger.info("Consolidated data passed schema validation.")
    except pa.errors.SchemaError as e:
        logger.error(f"Schema validation failed: {e}")
        # Proceeding anyways to allow manual inspection of failures, but logging error

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_concat.to_csv(output_path, sep='~', encoding='utf-8', index=False)
    logger.info(f"Saved consolidated data to {output_path}")
