from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pyperclip
import time
from dotenv import load_dotenv
# from selenium import webdriver
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import asyncio
from utils import saveScreenshot
from message import getMessage
import pickle
import json

load_dotenv()
import os

messageContainerXPath = '[aria-roledescription="Message"]'
scrollerXPath = '//*[@dir="ltr" and @data-jump-section="global"]'


# def initializeDriver(waitTime):
#     options = Options()
#     options.add_experimental_option("detach", True)
#     options.add_argument("--disable-logging")  # Disable logs
#     options.add_argument("--log-level=3")
#     options.add_argument(
#         "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
#     )
#     # options.add_argument("--headless")
#     options.add_argument("--window-size=1920,1080")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--no-sandbox")
#     driver = webdriver.Chrome(options=options)
#     wait = WebDriverWait(driver, waitTime)
#     return driver, wait


# def initializeDriver(waitTime):
#     proxy = "193.3.176.193:12323"  # Proxy IP and port
#     username = "14aa03e117adf"  # Proxy username
#     password = "f857a569b9"  # Proxy password
#     proxy_auth = f"https://{proxy}:{username}@{password}"

#     options = Options()
#     options.add_experimental_option("detach", True)
#     options.add_argument("--disable-logging")  # Disable logs
#     options.add_argument("--log-level=3")
#     options.add_argument(
#         "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
#     )
#     # options.add_argument("--headless")
#     options.add_argument("--window-size=1920,1080")
#     options.add_argument("--disable-dev-shm-usage")
#     options.add_argument("--no-sandbox")
#     options.add_argument(
#         f"--proxy-server={proxy_auth}"
#     )  # Add the proxy with authentication

#     driver = webdriver.Chrome(options=options)
#     wait = WebDriverWait(driver, waitTime)
#     return driver, wait


def initializeDriver(waitTime):
    proxy = "193.3.176.193:12323"  # Proxy IP and port
    username = "14aa03e117adf"  # Proxy username
    password = "f857a569b9"  # Proxy password

    # Configure proxy with authentication
    seleniumwire_options = {
        "proxy": {
            "http": f"http://{username}:{password}@{proxy}",
            "https": f"https://{username}:{password}@{proxy}",
            "no_proxy": "localhost,127.0.0.1",  # Exclude local addresses
        }
    }

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

    # Initialize the driver with selenium-wire options
    driver = webdriver.Chrome(
        options=options, seleniumwire_options=seleniumwire_options
    )
    wait = WebDriverWait(driver, waitTime)
    return driver, wait


def addCookies(driver):
    driver.get(f"https://discord.com/app")
    with open("cookies.json", "r") as f:
        cookies = json.load(f)
        for cookie in cookies:
            cookie["domain"] = "discord.com"  # Force domain if needed
            driver.add_cookie(cookie)
    driver.get("https://discord.com/channels/@me")
    driver.refresh()

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
