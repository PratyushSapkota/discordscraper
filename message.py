from bs4 import BeautifulSoup


def formatMessage(message, username, replyingTo=None, replyingAt=None):
    if replyingTo:
        output = f"{replyingTo}: \n{replyingAt} \n\n{username} replied: \n{message}"

    else:
        output = f"{username}: \n{message}"

    return output


def getMessage(messageElement: BeautifulSoup):
    messages = messageElement.select('div[id^="message-content-"]')
    usernames = messageElement.select('span[class^="username_"]')

    if len(messages) == 1:
        message = messages[0].text
        username = usernames[0].text
        finalOutput = formatMessage(message=message, username=username)
    else:
        replyingAt = messages[0].text
        username = usernames[1].text
        replyingTo = usernames[0].text
        message = messages[1].text
        finalOutput = formatMessage(
            message=message,
            username=username,
            replyingAt=replyingAt,
            replyingTo=replyingTo,
        )

    return finalOutput
