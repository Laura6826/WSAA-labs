from github import Github
from config import config as cfg

apikey = cfg["testgithubkey"]

g = Github(apikey)

#for repo in g.get_user().get_repos():
#print(repo.name)
repo = g.get_repo("Laura6826/wsaa_test")
#print(repo.clone_url)
fileInfo = repo.get_contents("test.txt")
urlOfFile = fileInfo.download_url
#print (urlOfFile)
response = requests.get(urlOfFile)
contentOfFile = response.text
print (contentOfFile)