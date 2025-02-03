from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
import json
import time
from seleniumFunctions import (
    login,
    scrapeChannelMessages,
)
from datetime import datetime
import asyncio
from utils import saveScreenshot

lastMessage = ""


async def scrapeMessages(driver: webdriver.Chrome, wait, scrapeServerChannel):
    global lastMessage
    data = []
    try:
        driver.get(f"https://discord.com/channels/{scrapeServerChannel}")
        try:
            await login(wait=wait, driver=driver)
        except Exception as e:
            pass
        
        messages = await scrapeChannelMessages(driver=driver, wait=wait)
        messages.reverse()
        for message in messages:
            if lastMessage == message:
                break
            data.append(message)

        if len(data) != 0:
            print("LATEST MESSAGE: ", data[0])
            lastMessage = data[0]

    except Exception as e:
        print("ERROR: ", e)

    return data
