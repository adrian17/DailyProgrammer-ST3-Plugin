import sublime, sublime_plugin

import os
from urllib.request import urlopen, Request
import json

# ============== CONFIG ===============

challengesPath = r"C:\DailyProgrammerChallenges"

fileName = "main.py"

initialContents = \
"""# {challengeTitle}
# {challengeUrl}


def main():
    pass


if __name__ == "__main__":
    main()
"""

readmeContents = \
"""[{challengeTitle}]({challengeUrl})
{challengeDesc}
"""

# initial cursor position after the file has been opened
# remember that title and url will occupy extra two lines
initialCursor = (6, 9)

# ============== CONFIG ===============

# valid characters for path
validChars = '-_.()[]! abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def updateChallenges(challenges, limit):
    newChallenges = []
    after = ""
    while after is not None:
        request = Request(
            "https://www.reddit.com/r/dailyprogrammer/new.json?limit=%s&after=%s" % (limit, after),
            data=None, 
            headers={
                'User-Agent': 'ST3 plugin for /r/DailyProgrammer'
            }
        )
        data = urlopen(request).readall()
        data = json.loads(data.decode())["data"]
        after = data["after"]
        posts = [post["data"] for post in data["children"] if "challenge #" in post["data"]["title"].lower()]
        posts = [{
            "title": post["title"],
            "desc" : post["selftext"],
            "url": post["url"]} for post in posts]

        challengeTitles = list(map(lambda c: c["title"], challenges))
        if any(post["title"] in challengeTitles for post in posts):
            posts = [post for post in posts if post["title"] not in challengeTitles]
            # we've encountered posts that are already stored, so no need to load older challenges
            after = None

        newChallenges = newChallenges + posts

    return newChallenges + challenges

def getAllChallenges():
    config = sublime.load_settings('DailyProgrammer.sublime-settings')
    challenges = config.get("challenges", [])

    challenges = updateChallenges(challenges, 100 if challenges==[] else 10)

    config.set("challenges", challenges)
    sublime.save_settings('DailyProgrammer.sublime-settings')

    return challenges


def startChallenge(window, title, url, desc):
    contents = initialContents.format(
        challengeTitle = title,
        challengeUrl = url
    )

    readme = readmeContents.format(
        challengeTitle = title,
        challengeUrl = url,
        challengeDesc = desc
    )

    folderName = title[title.index("#")+1:]
    folderName = "".join(c for c in folderName if c in validChars)

    folderPath = os.path.join(challengesPath, folderName)
    filePath = os.path.join(folderPath, fileName)
    readmePath = os.path.join(folderPath, "README.md")

    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
        with open(filePath, "w") as f:
            f.write(contents)
        with open(readmePath, "w") as f:
            f.write(readme)

    window.open_file(filePath + ":%s:%s" % initialCursor, sublime.ENCODED_POSITION)


class OldDailyProgrammerCommand(sublime_plugin.WindowCommand):
    def run(self):
        challenges = getAllChallenges()

        challengeNames = list(map(lambda challenge: challenge["title"], challenges))

        self.window.show_quick_panel(
            challengeNames,
            lambda i: startChallenge(self.window, challenges[i]["title"], challenges[i]["url"], challenges[i]["desc"]) if i != -1 else None)


class NewestDailyProgrammerCommand(sublime_plugin.WindowCommand):
    def run(self):
        challenges = getAllChallenges()

        newest = challenges[0]

        startChallenge(self.window, newest["title"], newest["url"], newest["desc"])
