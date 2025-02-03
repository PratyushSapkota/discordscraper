from selenium import webdriver
import os
import json

screenshotDirectory = "./screenshots"
lastMessageFile = "./lastMessage.json"


def getFileCount():
    files = [
        f
        for f in os.listdir(screenshotDirectory)
        if os.path.isfile(os.path.join(screenshotDirectory, f))
    ]

    return len(files)


def saveScreenshot(description, driver: webdriver.Chrome):
    fileCount = getFileCount()
    screenshotFileName = f"{description}_{fileCount}.png"
    driver.save_screenshot(f"{screenshotDirectory}/{screenshotFileName}")
    print(f"Saved Screenshot: {screenshotFileName}")


def clearScreenshotDirectory():
    for filename in os.listdir(screenshotDirectory):
        file_path = os.path.join(screenshotDirectory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")


def initialize_last_message_file():
    try:
        with open(lastMessageFile, "r") as file:
            json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(lastMessageFile, "w") as file:
            json.dump({"lastMessage": ""}, file, indent=4)


def store_message(message):
    data = {"lastMessage": message}
    with open(lastMessageFile, "w") as file:
        json.dump(data, file, indent=4)


def get_last_message():
    with open(lastMessageFile, "r") as file:
        data = json.load(file)
    return data.get("lastMessage", "")
