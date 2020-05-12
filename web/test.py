from bs4 import BeautifulSoup as b
import urllib3 as url

searchTerm = "tennis"
link = 'http://conceptnet.io/c/en/'
link = link + searchTerm
http_pool = url.connection_from_url(link)
r = http_pool.urlopen('GET', link)
http_pool.close()
html = r.data.decode('utf-8')
soup = b(html, features="html5lib")

termsWithContext = []
withContext = []
fart = []
candies = []

divs = soup.findAll("a")

for d in divs:
    if d.contents[0] == 'Terms with this context':
        withContext = d.find_parent().find_parent()

if len(withContext) > 0:
    links = withContext.findAll("span")
    for i in links:
        # print(i)
        if 'en' in i.contents[0]:

            l = i.find_parent().find_all("a")
            for j in l:
                print(j.contents[0])
        # print('en' in i.contents[0])

    # for i in dinks:
    #     print(i.contents[0])

