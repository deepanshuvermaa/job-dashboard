"""
Multi-source job board scrapers
Supports: Greenhouse, Ashby, Lever, Wellfound, Workable, DailyRemote, RemoteFront, Reddit,
          Darwinbox, StructuredData, GenericHTML
"""

from .base_scraper import BaseBoardScraper
from .greenhouse_scraper import GreenhouseScraper
from .ashby_scraper import AshbyScraper
from .lever_scraper import LeverScraper
from .wellfound_scraper import WellfoundScraper
from .workable_scraper import WorkableScraper
from .dailyremote_scraper import DailyRemoteScraper
from .remotefront_scraper import RemoteFrontScraper
from .reddit_scraper import RedditScraper
from .darwinbox_scraper import DarwinboxScraper
from .structured_data_scraper import StructuredDataScraper
from .generic_html_scraper import GenericHTMLScraper

SCRAPER_MAP = {
    'greenhouse': GreenhouseScraper,
    'ashby': AshbyScraper,
    'lever': LeverScraper,
    'wellfound': WellfoundScraper,
    'workable': WorkableScraper,
    'dailyremote': DailyRemoteScraper,
    'remotefront': RemoteFrontScraper,
    'reddit': RedditScraper,
    'darwinbox': DarwinboxScraper,
    'structured_data': StructuredDataScraper,
    'generic': GenericHTMLScraper,
    'eightfold': GenericHTMLScraper,
    'freshteam': GenericHTMLScraper,
    'career_page': GenericHTMLScraper,
}
