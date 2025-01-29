from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pyperclip
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import asyncio

load_dotenv()
import os


def initializeDriver():
    options = Options()
    # options.add_experimental_option("detach", True)
    options.add_argument("--disable-logging")  # Disable logs
    options.add_argument("--log-level=3")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    )
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 30)
    return driver, wait


async def login(wait, driver):
    print("Waintng for email box to load up")
    try:
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, '[aria-label="Email or Phone Number"]')
            )
        )
    except Exception as e:
        return
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


async def lookup(wait, driver, filter):
    print("SENDING FILTER")
    wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-block="true"]')))
    await asyncio.sleep(1)
    driver.find_element(By.XPATH, '//div[@data-block="true"]').click()
    await asyncio.sleep(1)
    pyperclip.copy(filter)
    driver.find_element(By.XPATH, '//div[@data-block="true"]').send_keys(
        Keys.CONTROL, "v"
    )
    await asyncio.sleep(1)
    driver.find_element(By.XPATH, '//div[@data-block="true"]').send_keys(Keys.RETURN)
    await asyncio.sleep(2)
    print("Sent filter")


async def getToPage(targetPage, driver, wait, filter, isFromFailure: bool = False):
    if isFromFailure:
        print(f"Reloading for page {targetPage}")
        driver.refresh()
        lookup(wait, driver, filter)

    wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//h2[@data-text-variant='heading-sm/semibold']")
        )
    )
    driver.find_element(
        By.XPATH, "//h2[@data-text-variant='heading-sm/semibold']"
    ).click()
    driver.find_element(By.CLASS_NAME, "inputMini_f8bc55").send_keys(targetPage)
    await asyncio.sleep(0.5)
    driver.find_element(By.CLASS_NAME, "inputMini_f8bc55").send_keys(Keys.ENTER)
    print("Pressed Enter")


def getMessage(sentInfoDiv, message, replying):
    sentInfo = sentInfoDiv.split("—")
    username = sentInfo[0]
    timeStamp = sentInfo[1]
    if replying:
        print("Is Replying")
        replyingUser = replying.find("div", class_="username_f9f2ca").text
        replyingMessage = replying.find("div", class_="repliedTextPreview_f9f2ca").text
        res = f"{replyingUser}: \n{replyingMessage} \n\n{username} replied: \n{message}"
    else:
        res = f"{username}: \n{message}"
    return res


# async def check(driver, wait: WebDriverWait):
#     data = []
#     print("Waiting for 1 message")
#     wait.until(EC.presence_of_element_located((By.CLASS_NAME, "message_ddc613")))
#     print("Found")
#     soup = BeautifulSoup(driver.page_source, "html.parser")
#     div_elements = soup.find_all("div", class_="message_ddc613")
#     if len(div_elements) == 0 or not div_elements:
#         print("IS THIS WHAT I THINK IT IS")
#         print("divelements: \n", div_elements)
#         pyperclip.copy(soup)
#         print("HTML COPIED")
#         return None
#     print("DIV ELEMENTS: ", len(div_elements))
#     for div in div_elements:
#         try:
#             message = getMessage(
#                 sentInfoDiv=div.find("h2", attrs={"class": "header_f9f2ca"}).text,
#                 message=div.find(
#                     "div", attrs={"class": "markup_f8f345 messageContent_f9f2ca"}
#                 ).text,
#                 replying=div.find("div", attrs={"class": "repliedMessage_f9f2ca"}),
#             )
#             data.append(message)
#         except Exception as e:
#             print("Error while parsing the message: ", e)
#     return data


async def scrapeChannelMessages(driver: webdriver.Chrome, wait: WebDriverWait):
    data = []

    messageContainerClass = "message_d5deea"
    sentInfoClass = "header_f9f2ca"
    messageClass = "markup_f8f345 messageContent_f9f2ca"
    replyClass = "repliedMessage_f9f2ca"

    wait.until(EC.presence_of_element_located((By.CLASS_NAME, messageContainerClass)))
    soup = BeautifulSoup(driver.page_source, "html.parser")
    messageContainers = soup.find_all("div", class_=messageContainerClass)

    for messageContainer in messageContainers:
        sentInfo = messageContainer.find("h3", class_=sentInfoClass)
        sentMessage = messageContainer.find("div", class_=messageClass)
        reply = messageContainer.find("div", class_=replyClass)

        username = sentInfo.text.split("—")[0]
        message = sentMessage.text

        finalMessage = f"{username}:\n{message}"

        if reply:
            repliedToUser = reply.find("span", class_="username_f9f2ca")
            repliedMessage = reply.find(
                "div",
                class_="repliedTextContent_f9f2ca markup_f8f345 messageContent_f9f2ca",
            )
            if repliedToUser:
                finalMessage = f"{repliedToUser.text}:\n{repliedMessage.text}\n\n{username} replied:\n{message}"

        data.append(finalMessage)
    return data


# async def forceGet1Page(driver, wait, checkingPage, failures, failureUntilWait):
#     while True:
#         res = check(driver, checkingPage, wait)
#         if res is not None:
#             return res

#         failures += 1
#         if failureUntilWait >= failures:
#             print("Waiting for 30 seconds")
#             await asyncio.sleep(30)
#             failures = 0

#         getToPage(targetPage=checkingPage, driver=driver, wait=wait, isFromFailure=True)
#         await asyncio.sleep(1)


# repliedMessage_f9f2ca
