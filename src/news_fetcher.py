import requests
from collections import defaultdict
import datetime
import time
import random
from typing import Optional

from bs4 import BeautifulSoup

from config import LINK_OKX_NEWS, LINK_OKX_NEWS_PAGE, LOGGER


def fetch_news(url: str = LINK_OKX_NEWS) -> defaultdict[datetime.date, list[str]]:
    """
    Fetches news items from the given webpage URL and returns a dictionary 
    with dates as keys and corresponding URLs as values.
    """
    LOGGER.info(f"Fetching news from URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        LOGGER.error(f"Failed to fetch the webpage. Status code: {response.status_code}")
        raise Exception(f"Failed to fetch the webpage. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract relevant information
    news_dict = defaultdict(list)
    for article in soup.select('.index_articleItem__d-8iK'):
        link_tag = article.find('a', href=True)
        link = link_tag['href'] if link_tag else None

        date_tag = article.find('span', text=lambda t: t and t.startswith('Published on'))
        date_text = date_tag.text.replace('Published on ', '') if date_tag else None
        date = datetime.datetime.strptime(date_text, '%b %d, %Y').date() if date_text else None

        if link and date:
            news_dict[date].append(link)
            LOGGER.debug(f"Added link: {link} for date: {date}")

    LOGGER.info(f"Fetched {len(news_dict)} news items.")
    return news_dict


def get_max_page(url: str = LINK_OKX_NEWS) -> int:
    """Fetches the maximum pagination number from the given webpage URL."""
    LOGGER.info(f"Fetching max page number from URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        LOGGER.error(f"Failed to fetch the webpage. Status code: {response.status_code}")
        raise Exception(f"Failed to fetch the webpage. Status code: {response.status_code}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    pagination_numbers = [int(link.text) for link in soup.find_all('a') if link.text.isdigit()]
    max_page = max(pagination_numbers)
    LOGGER.info(f"Max page number found: {max_page}")
    return max_page


def get_date_news_matching(max_pages: Optional[int] = None) -> defaultdict[datetime.date, list[str]]:
    """Fetches the news items with dates as keys and corresponding URLs as values."""
    if max_pages is None:
        LOGGER.info("Max pages not provided, fetching from get_max_page.")
        max_pages = get_max_page()

    LOGGER.info(f"Fetching news for {max_pages} pages.")
    news_dict = defaultdict(list)
    for page_num in range(1, max_pages + 1):
        LOGGER.info(f"Fetching news for page {page_num}.")
        news_page = fetch_news(LINK_OKX_NEWS_PAGE + f"{page_num}")
        for date, links in news_page.items():
            news_dict[date].extend(links)
            LOGGER.debug(f"Updated news_dict for date: {date} with {len(links)} links.")
        time.sleep(random.uniform(0.1, 2))
    logging_info = {dt: len(links) for dt, links in news_dict.items()}
    LOGGER.info(f"Total news items fetched: {logging_info}")
    print(news_dict)
    return news_dict


# # Example usage
# url = "https://www.okx.com/help/section/announcements-latest-announcements/page/4"
# news = fetch_news(url)
# print(news)

# # Example usage
# url = "https://www.okx.com/help/section/announcements-latest-announcements/page/1"
# max_page = get_max_page(url)
# print(max_page)

# print(get_date_news_matching(3))
