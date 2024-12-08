import os
import logging
from dotenv import load_dotenv

from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
LOGGER = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables")

# Global variables
LINK_OKX_NEWS = "https://www.okx.com/help/category/announcements"
LINK_OKX_NEWS_PAGE = "https://www.okx.com/help/section/announcements-latest-announcements/page/"
MAX_SCROLLS = 10
MAX_PAGES = 3

OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)
MAX_TOKENS = 10000

SYSTEM_PROMPT = (
    "You are an intelligent assistant capable of analyzing visual content from website screenshots. "
    "Your role is to extract meaningful and structured information such as titles, dates, and text content from the provided visual input. "
    "Focus on providing accurate results while maintaining the original structure and details visible in the image."
)

USER_PROMPT = (
    "Analyze the provided screenshot and extract the following information: "
    "1. Title: The title of the page or article, as shown in the screenshot; "
    "2. Date: The date of publication, exactly as it appears in the screenshot; "
    "3. Text: The complete text content of the publication, without paraphrasing or modifying the original text. "
    "Ensure that the extracted information matches the screenshot accurately and is clearly formatted in JSON with fields: "
    "'title': str, 'date': datetime.date, 'text': str."
)