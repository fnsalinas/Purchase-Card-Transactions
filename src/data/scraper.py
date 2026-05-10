import logging
import os
import urllib.request
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from contextlib import closing

logger = logging.getLogger(__name__)

def get_excel_urls(browser):
    """
    Extracts Excel URLs from the Birmingham city council dataset page.
    """
    resource_list = BeautifulSoup(browser.page_source, 'html.parser').find('ul', {'class': 'resource-list'})
    if not resource_list:
        logger.warning("Resource list not found on the page.")
        return []
    
    resource_items = resource_list.find_all('li', {'class': 'resource-item'})
    items = []
    for item in resource_items:
        a_tag = item.find('a', {'class': 'resource-url-analytics'})
        if a_tag and a_tag.get('href'):
            items.append(a_tag['href'])
    return items

def scrape_data(output_dir='data/raw', headless=True):
    """
    Downloads purchase card transaction files.
    """
    os.makedirs(output_dir, exist_ok=True)
    main_url = 'https://data.birmingham.gov.uk/dataset/purchase-card-transactions'
    
    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    if headless:
        options.add_argument('--headless')
        
    logger.info(f"Starting browser to scrape {main_url}")
    
    service = ChromeService(ChromeDriverManager().install())
    with closing(Chrome(service=service, options=options)) as browser:
        browser.get(main_url)
        urls = get_excel_urls(browser)
        
        logger.info(f"Found {len(urls)} files to download.")
        for file_url in urls:
            file_name = file_url.split('/')[-1]
            output_path = os.path.join(output_dir, file_name)
            
            if not os.path.exists(output_path):
                logger.info(f'Downloading {file_name}...')
                try:
                    urllib.request.urlretrieve(file_url, output_path)
                except Exception as e:
                    logger.error(f"Failed to download {file_name}: {e}")
            else:
                logger.info(f'{file_name} already exists. Skipping.')
                
    logger.info('Scraping complete.')
