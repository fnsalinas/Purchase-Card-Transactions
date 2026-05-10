# -*- coding: utf-8 -*-
import click
import logging
from pathlib import Path
from dotenv import find_dotenv, load_dotenv

from src.data.scraper import scrape_data
from src.data.consolidator import consolidate_data
from src.data.cleaner import clean_data

@click.command()
@click.option('--skip-scrape', is_flag=True, help="Skip downloading files from the web.")
def main(skip_scrape):
    """ Runs data processing scripts to turn raw data from (../raw) into
        cleaned data ready to be analyzed (saved in ../processed).
    """
    logger = logging.getLogger(__name__)
    
    # 1. Scrape
    if not skip_scrape:
        logger.info('Starting data scraping process...')
        scrape_data(output_dir='data/raw', headless=True)
    else:
        logger.info('Skipping scraping step.')

    # 2. Consolidate
    logger.info('Consolidating raw files...')
    consolidate_data(input_dir='data/raw', output_path='data/interim/raw_consolidated_data.csv')
    
    # 3. Clean
    logger.info('Cleaning consolidated data...')
    clean_data(input_path='data/interim/raw_consolidated_data.csv', output_path='data/interim/prepared_consolidated_data.csv')
    
    logger.info('Data pipeline finished successfully.')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv())

    main()
