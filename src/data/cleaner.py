import logging
import os
import pandas as pd

logger = logging.getLogger(__name__)

def clean_data(input_path='data/interim/raw_consolidated_data.csv', output_path='data/interim/prepared_consolidated_data.csv'):
    """
    Cleans and prepares the consolidated data for analysis/modeling.
    Handles imputations, duplicates, and text normalizations.
    """
    logger.info(f"Cleaning data from {input_path}")
    
    if not os.path.exists(input_path):
        logger.error(f"Input file {input_path} not found.")
        return

    df = pd.read_csv(input_path, sep='~', encoding='utf-8', low_memory=False)
    
    # 1. Drop rows without a transaction date
    df.dropna(subset=['trans_date'], inplace=True)

    # 2. Complete directorate using 'unnamed' column if directorate is null
    df['directorate_completed'] = df.apply(
        lambda x: x['unnamed'] if pd.isna(x['directorate']) and not pd.isna(x['unnamed']) else x['directorate'],
        axis=1
    )
    
    # Drop columns that are heavily null or redundant now
    cols_to_drop = ['unnamed', 'directorate', 'original_cur', 'billing_gross_amt', 
                    'billing_cur_code', 'billing_cur_code_1', 'trans_tax_amt', 'trans_vat_desc']
    existing_drops = [c for c in cols_to_drop if c in df.columns]
    df.drop(columns=existing_drops, inplace=True)

    # 3. Impute trans_cac_code_1 based on trans_cac_code_2
    if 'trans_cac_code_2' in df.columns and 'trans_cac_code_1' in df.columns:
        df_to_impute = df.groupby(['trans_cac_code_2', 'trans_cac_code_1'], as_index=False)['sheet_name'].count()\
            .sort_values(by='sheet_name', ascending=False)\
            .drop_duplicates(subset='trans_cac_code_2', keep='first')\
            .rename(columns={'sheet_name':'#'})
        
        df = pd.merge(df, df_to_impute[['trans_cac_code_2', 'trans_cac_code_1']], how='left', on='trans_cac_code_2', suffixes=('', '_y'))
        df['trans_cac_code_1_imputed'] = df.apply(
            lambda x: x['trans_cac_code_1_y'] if pd.isna(x['trans_cac_code_1']) else x['trans_cac_code_1'], axis=1
        )
        
        # Impute trans_cac_desc_1
        cols = ['trans_cac_code_1', 'trans_cac_desc_1', 'sheet_name']
        if all(c in df.columns for c in cols):
            df_trans_cac_1 = df[cols].groupby(cols[:-1], as_index=False)[cols[-1]].count()\
                .sort_values(by='sheet_name', ascending=False).rename(columns={'sheet_name':'#'})
            df = pd.merge(df, df_trans_cac_1[['trans_cac_code_1', 'trans_cac_desc_1']], how='left', on='trans_cac_code_1', suffixes=('', '_y'))
            df['trans_cac_desc_1_imputed'] = df['trans_cac_desc_1_y']
        else:
            df['trans_cac_desc_1_imputed'] = df['trans_cac_desc_1'] if 'trans_cac_desc_1' in df.columns else None
    else:
        df['trans_cac_code_1_imputed'] = df['trans_cac_code_1'] if 'trans_cac_code_1' in df.columns else None
        df['trans_cac_desc_1_imputed'] = df['trans_cac_desc_1'] if 'trans_cac_desc_1' in df.columns else None

    # 4. Impute trans_cac_code_2 based on trans_cac_code_3
    if 'trans_cac_code_3' in df.columns and 'trans_cac_code_2' in df.columns:
        df_to_impute_2 = df.groupby(['trans_cac_code_3', 'trans_cac_code_2'], as_index=False)['sheet_name'].count()\
            .sort_values(by='sheet_name', ascending=False)\
            .drop_duplicates(subset='trans_cac_code_3', keep='first')\
            .rename(columns={'sheet_name':'#'})
            
        df = pd.merge(df, df_to_impute_2[['trans_cac_code_3', 'trans_cac_code_2']], how='left', on='trans_cac_code_3', suffixes=('', '_y'))
        df['trans_cac_code_2_imputed'] = df.apply(
            lambda x: x['trans_cac_code_2_y'] if pd.isna(x['trans_cac_code_2']) else x['trans_cac_code_2'], axis=1
        )
        
        # Impute trans_cac_desc_2
        cols2 = ['trans_cac_code_2', 'trans_cac_desc_2', 'sheet_name']
        if all(c in df.columns for c in cols2):
            df_trans_cac_2 = df[cols2].groupby(cols2[:-1], as_index=False)[cols2[-1]].count()\
                .sort_values(by='sheet_name', ascending=False).rename(columns={'sheet_name':'#'})
            df = pd.merge(df, df_trans_cac_2[['trans_cac_code_2', 'trans_cac_desc_2']], how='left', on='trans_cac_code_2', suffixes=('', '_y'))
            df['trans_cac_desc_2_imputed'] = df['trans_cac_desc_2_y']
        else:
             df['trans_cac_desc_2_imputed'] = df['trans_cac_desc_2'] if 'trans_cac_desc_2' in df.columns else None
    else:
        df['trans_cac_code_2_imputed'] = df['trans_cac_code_2'] if 'trans_cac_code_2' in df.columns else None
        df['trans_cac_desc_2_imputed'] = df['trans_cac_desc_2'] if 'trans_cac_desc_2' in df.columns else None

    # Keep only relevant columns
    final_cols = ['file_name', 'sheet_name', 'trans_date', 'original_gross_amt', 'merchant_name', 'card_number', 
                  'trans_cac_code_1_imputed', 'trans_cac_desc_1_imputed', 
                  'trans_cac_code_2_imputed', 'trans_cac_desc_2_imputed', 'directorate_completed']
    
    existing_final = [c for c in final_cols if c in df.columns]
    df = df[existing_final].copy()

    # 5. Fill remaining NAs with mode
    fill_cols = ['trans_cac_code_1_imputed', 'trans_cac_desc_1_imputed', 
                 'trans_cac_code_2_imputed', 'trans_cac_desc_2_imputed', 'directorate_completed']
    for col in fill_cols:
        if col in df.columns and not df[col].mode().empty:
            df[col] = df[col].fillna(df[col].mode().values[0])

    # 6. Drop duplicates
    logger.info(f'Shape before drop duplicates: {df.shape}')
    df.drop_duplicates(subset=None, keep='first', inplace=True, ignore_index=True)
    logger.info(f'Shape after drop duplicates: {df.shape}')

    # Drop intermediate columns
    if 'trans_cac_code_1_imputed' in df.columns:
        df.rename(columns={'trans_cac_code_1_imputed': 'trans_cac_code_1', 'trans_cac_desc_1_imputed': 'trans_cac_desc_1',
                           'trans_cac_code_2_imputed': 'trans_cac_code_2', 'trans_cac_desc_2_imputed': 'trans_cac_desc_2',
                           'directorate_completed': 'directorate'}, inplace=True)
    
    # 7. Convert trans_date
    if 'trans_date' in df.columns:
        df['trans_date'] = pd.to_datetime(df['trans_date'], errors='coerce')
        df.dropna(subset=['trans_date'], inplace=True) # drop if it wasn't a valid date

    # 8. Standardize merchant names
    corrections = [
        ('amazon', 'Amazon'), ('travelodge', 'Travelodge'), ('asda', 'Asda'), ('argos', 'Argos'), 
        ('esso', 'ESSO'), ('texaco', 'Texaco'), ('sainsburys', 'Sainsburys'), ('tesco', 'Tesco'),
        ('itunes', 'Itunes'), ('mcdonalds', 'MCDonalds'), ('weoley castle', 'Weoley Castle'), 
        ('w m morrison', 'WM Morrison'), ('ikea', 'Ikea'), ('currys', 'Currys')
    ]
    if 'merchant_name' in df.columns:
        df['merchant_name'] = df['merchant_name'].astype(str)
        for pattern, correction in corrections:
            df['merchant_name'] = df['merchant_name'].apply(lambda x: correction if pattern in x.lower() else x)

    # Save prepared dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, sep='~', encoding='utf-8', index=False)
    logger.info(f"Saved prepared data to {output_path}")
