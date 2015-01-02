import sublime, sublime_plugin

import os
from urllib.request import urlopen, Request
import json

# ============== CONFIG ===============

challengesPath = r"C:\DailyProgrammerChallenges"

fileName = "main.py"

initialContents = """

def main():
    pass


if __name__ == "__main__":
    main()
"""

commentStyle = "# "
appendTitle = True
appendUrl = True

# initial cursor position after the file has been opened
# remember that title and url will occupy extra two lines
initialCursor = (6, 9)

# ============== CONFIG ===============

# valid characters for path
validChars = '-_.()[]! abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

class NewestDailyProgrammerCommand(sublime_plugin.WindowCommand):
    def run(self):

        request = Request(
            "https://www.reddit.com/r/dailyprogrammer/new.json", 
            data=None, 
            headers={
                'User-Agent': 'ST3 plugin for /r/DailyProgrammer'
            }
        )

        data = urlopen(request).readall()
        posts = json.loads(data.decode())["data"]["children"]
        newest = [post["data"] for post in posts if "Challenge #" in post["data"]["title"]][0]

        challengeTitle = newest["title"]
        challengeUrl = newest["url"]

        contents = []
        if appendTitle:
            contents.append(commentStyle + challengeTitle)
        if appendUrl:
            contents.append(commentStyle + challengeUrl)
        contents.append(initialContents)
        contents = "\n".join(contents)

        folderName = challengeTitle[challengeTitle.index("#")+1:]
        folderName = "".join(c for c in folderName if c in validChars)

        folderPath = os.path.join(challengesPath, folderName)
        filePath = os.path.join(folderPath, fileName)

        if not os.path.exists(folderPath):
            os.mkdir(folderPath)
            with open(filePath, "w") as f:
                f.write(contents)

        self.window.open_file(filePath + ":%s:%s" % initialCursor, sublime.ENCODED_POSITION)
