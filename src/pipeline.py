from typing import Optional
import datetime
from collections import defaultdict
import json

from config import LINK_OKX_BASE, LOGGER
from news_fetcher import get_date_news_matching
from img_scraper import download_website, analyse_content


def get_news_pipelline(start_date: datetime.date, end_date: datetime.date, 
                       max_pages: Optional[int] = None) -> list[dict[str, str]]:
    """Fetches and processes news articles within a date range."""
    LOGGER.info(f"Starting get_news_pipelline with start_date={start_date}, "
                f"end_date={end_date}, max_pages={max_pages}")
    date_links = get_date_news_matching(max_pages)
    LOGGER.debug(f"Fetched date links: {date_links}")
    
    filtered_date_links = defaultdict(list)
    for date, link in date_links.items():
        if start_date <= date <= end_date:
            LOGGER.info(f"----{start_date} <= {date} <= {end_date}----")
            filtered_date_links[date].extend(link)
    LOGGER.debug(f"Filtered date links: {filtered_date_links}")

    filtered_news = []
    for date, links in filtered_date_links.items():
        for link in links:
            LOGGER.info(f"Processing date/link: {date}/{link}")
            full_link = LINK_OKX_BASE + link
            screenshot_base64 = download_website(full_link)
            analysis = analyse_content(screenshot_base64)
            analysis["link"] = full_link
            analysis["published_date"] = date.strftime("%Y-%m-%d")
            filtered_news.append(analysis)
            LOGGER.debug(f"Analysis result: {analysis}")
            # filtered_news.append("")

    LOGGER.info(f"Completed get_news_pipelline with {len(filtered_news)} items")
    return filtered_news


def compose_news_pipeline(start_date: datetime.date, end_date: datetime.date,
                          max_pages: Optional[int] = None) -> str:
    """Composes a JSON string of news articles within a date range."""
    LOGGER.info(f"Starting compose_news_pipeline with start_date={start_date}, "
                f"end_date={end_date}, max_pages={max_pages}")
    filtered_news = get_news_pipelline(start_date=start_date, end_date=end_date, 
                                       max_pages=max_pages)
    json_news = json.dumps(filtered_news, indent=4)
    LOGGER.info("Completed compose_news_pipeline")
    return json_news


# print(get_news_pipelline(start_date = datetime.date(2024, 11, 19), 
#                         end_date = datetime.date(2024, 11, 22), 
#                         max_pages = 3))