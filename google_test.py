import requests
from lxml import etree


url = 'https://www.google.com.hk/search?q=crystal laser cannon vs predator'
rst = requests.get(url)
with open('1.html', 'w', encoding='utf8')as f:
    f.write(rst.text)



html = etree.HTML(rst.text)
next = html.xpath('//footer/div[1]//a/@href')
next_url = 'https://www.google.com'+next[0]
print(next_url)

rst1 = requests.get(url)

with open('2.html','w',encoding='utf8')as f:
    f.write(rst1.text)


# rst1 = requests.get()