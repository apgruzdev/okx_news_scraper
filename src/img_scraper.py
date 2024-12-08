import os
import io
from typing import Any
import tempfile
import json

from config import (LOGGER, MAX_SCROLLS,
                    OPENAI_CLIENT, SYSTEM_PROMPT, USER_PROMPT, MAX_TOKENS)
from selenium import webdriver
import base64
from PIL import Image

# Create a reusable chrome options object
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")


def encode_image(image_path: str) -> str:
    """Encodes an image file into a base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def download_website(url: str, max_scrolls: int = MAX_SCROLLS) -> str:
    """Captures screenshots of a website by scrolling and combining them into one image."""
    driver = webdriver.Chrome(options=chrome_options)

    temp_dir = tempfile.mkdtemp()
    combined_image_path = os.path.join(temp_dir, "combined_screenshot.png")

    try:
        LOGGER.info(f"Navigating to {url}")
        driver.get(url)

        width, height = 1800, 1200
        driver.set_window_size(width, height)
        screenshots: list[bytes] = []
        current_scroll = 0

        while current_scroll < max_scrolls:
            LOGGER.info(f"Taking screenshot {current_scroll + 1}/{max_scrolls}")
            
            screenshot = driver.get_screenshot_as_png()
            screenshots.append(screenshot)

            # Save each screenshot chunk
            chunk_path = os.path.join(temp_dir, f"screenshot_{current_scroll + 1}.png")
            with open(chunk_path, "wb") as chunk_file:
                chunk_file.write(screenshot)
            LOGGER.info(f"Saved screenshot chunk at {chunk_path}")

            # Scroll down
            last_height = height * (current_scroll + 1)
            driver.execute_script(f"window.scrollTo(0, {last_height});")

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height <= last_height:
                LOGGER.info("Reached the end of the page")
                break
            current_scroll += 1

        # Combine screenshots into one image
        combined_height = sum(Image.open(io.BytesIO(img_data)).height for img_data in screenshots)
        max_width = max(Image.open(io.BytesIO(img_data)).width for img_data in screenshots)
        combined_image = Image.new("RGB", (max_width, combined_height))

        current_height = 0
        for img_data in screenshots:
            img = Image.open(io.BytesIO(img_data))
            combined_image.paste(img, (0, current_height))
            current_height += img.height

        combined_image.save(combined_image_path)
        LOGGER.info(f"Combined screenshot saved at {combined_image_path}")

        base64_image = encode_image(combined_image_path)
        LOGGER.info("Screenshot captured and encoded successfully")
        return base64_image

    finally:
        driver.quit()
        LOGGER.info(f"Temporary files saved in {temp_dir}")


def analyse_content(base64_image: str,
                    user_prompt: str = USER_PROMPT, system_prompt: str = SYSTEM_PROMPT, 
                    max_tokens: int = MAX_TOKENS) -> dict[str, Any]:
    """Analyzes content using OpenAI's chat API."""
    try:
        LOGGER.info("Preparing request to OpenAI chat API.")
        
        response_scoring = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a Helpful Assistant with the following characteristics: {system_prompt}. "
                    "Your task is to analyze the given website and provide a JSON response."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{user_prompt} Respond in JSON format."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ]
                },
            ],
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        LOGGER.info("Request successful, parsing response.")
        response_content = json.loads(response_scoring.model_dump_json())['choices'][0]['message']['content']
        return json.loads(response_content)
    
    except Exception as e:
        LOGGER.error(f"Error in analysing content: {str(e)}")
        raise e


# if __name__ == "__main__":
#     url_to_capture = "https://www.okx.com/help/web3"
#     # url_to_capture = "https://www.okx.com/help/okx-will-support-the-wise-monkey-monky-airdrop-for-apecoin-ape-and-floki"
#     screenshot_base64 = download_website(url_to_capture)
#     analysis = analyse_content(screenshot_base64)
#     for k, v in analysis.items():
#         print(f"{k}: {v}")
#     LOGGER.info("Script completed successfully")
