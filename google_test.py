import requests

url = 'https://www.google.com.hk/search?q=crystal laser cannon vs predator'
rst = requests.get(url)
with open('1.html', 'w', encoding='utf8')as f:
    f.write(rst.text)
