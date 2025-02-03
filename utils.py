from selenium import webdriver
import os

directory = "./screenshots"


def getFileCount():
    files = [
        f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))
    ]

    return len(files)


def saveScreenshot(description, driver: webdriver.Chrome):
    fileCount = getFileCount()
    screenshotFileName = f"{description}_{fileCount}.png"
    driver.save_screenshot(f"{directory}/{screenshotFileName}")
    print(f"Saved Screenshot: {screenshotFileName}")


def clearDirectory():
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")
