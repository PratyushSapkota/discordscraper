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
from utils import store_message, get_last_message


async def scrapeMessages(driver: webdriver.Chrome, wait, scrapeServerChannel):
    lastMessage = get_last_message()
    data = []
    try:
        try:
            await login(wait=wait, driver=driver)
        except Exception as e:
            print("888Failed to login888")
            print("\n", e)
            pass
        driver.get(f"https://discord.com/channels/{scrapeServerChannel}")

        messages = await scrapeChannelMessages(driver=driver, wait=wait)
        messages.reverse()
        for message in messages:
            if lastMessage == message:
                break
            data.append(message)

        if len(data) != 0:
            print("LATEST MESSAGE: ", data[0])
            lastMessage = data[0]
            store_message(lastMessage)

    except Exception as e:
        print(
            "ERROR: 99999999999999999999999999999999999999999999999999999999999999999\n\n",
            e,
        )

    return data
