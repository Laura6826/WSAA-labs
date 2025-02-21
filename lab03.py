import requests

url = 'https://jsonplaceholder.typicode.com/posts/1'
response = requests.delete(url)

# Print the status code
print