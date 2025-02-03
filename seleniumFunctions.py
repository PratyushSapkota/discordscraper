from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pyperclip
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import asyncio
from utils import saveScreenshot
from message import getMessage

load_dotenv()
import os

messageContainerXPath = '[aria-roledescription="Message"]'
scrollerXPath = '//*[@dir="ltr" and @data-jump-section="global"]'


def initializeDriver(waitTime):
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-logging")  # Disable logs
    options.add_argument("--log-level=3")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    )
    # options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, waitTime)
    return driver, wait


async def login(wait, driver: webdriver.Chrome):
    driver.get("https://discord.com/login")
    await asyncio.sleep(10)
    currentUrl = driver.current_url
    if "channels" in currentUrl:
        print("already logged in")
        return

    print("Waiting for email box to load up")
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[aria-label="Email or Phone Number"]')
        )
    )

    print("Sending Email")

    email_input = driver.find_element(
        By.CSS_SELECTOR, '[aria-label="Email or Phone Number"]'
    )
    email_input.send_keys(os.getenv("DISCORD_EMAIL"))

    print("Sending Pass")
    password_input = driver.find_element(By.CSS_SELECTOR, '[aria-label="Password"]')
    password_input.send_keys(os.getenv("DISCORD_PASSWORD"))
    print("Clicking Log In")
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    await asyncio.sleep(2)
    print("Clicked")


async def scrapeChannelMessages(driver: webdriver.Chrome, wait: WebDriverWait):
    data = []

    try:
        wait.until(EC.presence_of_element_located((By.XPATH, scrollerXPath)))
        scroller = driver.find_element(By.XPATH, scrollerXPath)
        if scroller.is_displayed():
            scroller.send_keys(Keys.END)

        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, messageContainerXPath))
        )

        saveScreenshot("Before Scraping", driver)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        messageContainers = soup.select(messageContainerXPath)

        for messageDivs in messageContainers:
            output = getMessage(messageDivs)
            data.append(output)

    except Exception as e:
        print("Failed somewhere while scraping; \n", e)
        pass
    print(f"Scrapped {len(data)} now scanning for new")
    return data
