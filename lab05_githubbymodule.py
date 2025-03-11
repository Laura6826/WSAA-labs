
from github import Github
import requests
from config import config as cfg

apikey = cfg["testgithubkey"]

try:
    g = Github(apikey)

    # List all repositories for the authenticated user
    for repo in g.get_user().get_repos():
        print(repo.name)

    # Get the specific repository and print its clone URL
    repo = g.get_repo("Laura6826/wsaa_test")
    print(repo.clone_url)

    # Get the contents of the file
    fileInfo = repo.get_contents("test.txt")
    urlOfFile = fileInfo.download_url
    response = requests.get(urlOfFile)
    contentOfFile = response.text

    # Update the file with new contents
    newContents = contentOfFile + " more stuff 2 \n"
    print(newContents)
    gitHubResponse = repo.update_file(fileInfo.path, "updated by prog", newContents, fileInfo.sha)
    print(gitHubResponse)

except Exception as e:
    print("An error occurred:", e)
