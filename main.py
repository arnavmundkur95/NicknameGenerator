import nltk as n
from bs4 import BeautifulSoup as b
import urllib3 as url
import random
import pronouncing as p
from metaphone import doublemetaphone as d
from nltk.corpus import wordnet as wn
import eel
import json
import threading
import time

#%% Functions and global variables

qs = [False, False, False, False]
global smalltalk
smalltalk = False
smalltalkies = ["Where are you from?", "Where do you currently live?", "Do you have any pets?", "Which sports do you play or follow?"]
asked = [False, False, False]
global firstName
global lastName
global middleName
global message
global rhymingNames
global key
rhymingNames = -1

qtexts = ["Lets start with the basics, what is your name?", "Which sports do you play or follow?", "Alright, do you follow or play any other sports?",
          "I see, and what about movies? Which genres do you like watching?",
          "Hmm could you maybe respell that, or try another one. Maybe make it singular instead of plural",
          "And finally, would you say that you like sports or movies more? You have to choose one!"]

def nounGetter(tags):
    nouns = []

    for j in tags:
        if j[1] == 'NN' or j[1] == "NNS" and j[0] not in nouns:
            nouns.append(j[0])

    return nouns


def verbGetter(tags):
    verbs = []

    for j in tags:
        if j[1] == 'VB' or j[1] == 'VBD' or j[1] == 'VBG' or j[1] == 'VBN' and j[0] not in verbs:
            verbs.append(j[0])

    return verbs


def getConceptTermsWithContext(word):
    link = 'http://conceptnet.io/c/en/'
    link = link + word
    http_pool = url.connection_from_url(link)
    r = http_pool.urlopen('GET', link)
    http_pool.close()
    html = r.data.decode('utf-8')
    soup = b(html, features='html.parser')

    termsWithContext = []
    withContext = []
    temps = []
    candies = []


    divs = soup.findAll("a")

    for d in divs:
        if d.contents[0] == 'Terms with this context':
            withContext = d.find_parent().find_parent()

    if len(withContext) > 0:
        links = withContext.findAll("span")
        for k in links:
            if 'en' in k.contents[0]:
                l = k.find_parent().find_all("a")
                for j in l:
                    termsWithContext.append(n.word_tokenize(j.contents[0]))

        if len(termsWithContext) > 1:
            del (termsWithContext[0])

        for k in termsWithContext:
            if len(k) == 1 and not '➜' == k[0] and not k[0] == 'v' and not k[0] == 'n':
                temps.append(k[0])

            elif len(k) > 1 and not k[0] == 'v' and not k[0] == 'n' and not k[0] == 'a' and not 'more' in k[0].lower():
                temp = ""
                for l in k:
                    if not l == ',':
                        temp = temp + " " + l
                temps.append(temp[1:])

        termsWithContext = temps

        for i in range(len(termsWithContext)):

            if " " in termsWithContext[i]:
                termsWithContext[i] = termsWithContext[i].replace(" ", "_")
            elif "-" in termsWithContext[i]:
                termsWithContext[i] = termsWithContext[i].replace("-", "_")
            try:
                termsWithContext[i] = termsWithContext[i].encode()
                termsWithContext[i] = termsWithContext[i].decode('UTF-8')
            except UnicodeDecodeError:
                continue
            link = 'http://conceptnet.io/c/en/' + termsWithContext[i]
            http_pool = url.connection_from_url(link)
            r = http_pool.urlopen('GET', link)
            htm = r.data.decode('UTF-8')
            http_pool.close()
            s = b(htm, features='html.parser')

            fibs = s.findAll("a")

            for j in fibs:
                if j.contents[0] == 'Context of this term':
                    lin = j.find_parent().find_parent()

                    if len(lin) > 0:

                        ls = lin.findAll("a")
                        pre = []
                        for k in range(len(ls)):
                            term = n.word_tokenize(ls[k].contents[0])

                            if len(term) == 1 and not '➜' == term[0] and not term[0] == 'v' and not term[0] == 'n':
                                pre.append(term[0])

                            elif len(term) > 1 and not term[0] == 'v' and not term[0] == 'n' and not term[0] == 'a' and not 'more' in \
                                term[0].lower():
                                temp = ""
                                for l in term:
                                    if not l == ',':
                                        temp = temp + " " + l
                                pre.append(temp[1:])
                        del(pre[0])
                        pre = list(set(pre))

                        if word in pre and len(pre) < 3:
                            if "_" in termsWithContext[i]:
                                temp = termsWithContext[i]
                                temp = temp.replace("_", " ")
                                candies.append(temp)
                            else:
                                candies.append(termsWithContext[i])

    candies = list(set(candies))
    c = []
    for i in candies:
        if not word in i:
            c.append(i)
    candies = c

    return candies


def getConceptDerivedTerms(word):
    searchTerm = word
    link = 'http://conceptnet.io/c/en/'
    link = link + searchTerm
    http_pool = url.connection_from_url(link)
    r = http_pool.urlopen('GET', link)
    http_pool.close()
    html = r.data.decode('utf-8')
    soup = b(html, features="html5lib")

    divs = soup.findAll("a")
    div = []
    candies = []

    for d in divs:
        if d.contents[0] == 'Derived terms':
            div = d.find_parent().find_parent()

    if len(div) > 0:
        links = div.findAll("a")
        for k in links:
            candies.append(n.word_tokenize(k.contents[0]))

        del (candies[0])

        c = []

        for k in candies:
            if len(k) > 1:
                counter = 0
                s = ''
                for j in k:
                    if len(j) > 2:
                        counter += 1
                        s = s + ' ' + j
                if counter == len(k):
                    c.append(s)

            elif len(k[0]) > 2:
                c.append(k[0])

        candies = c
        c = []

        for k in candies:
            if not k == searchTerm:
                c.append(k)
        candies = c

        for k in range(len(candies)):
            temp = n.word_tokenize(candies[k])
            if len(temp) > 1:
                s = ''
                for j in temp:
                    s = s + j + ' '
                candies[k] = s
            else:
                candies[k] = temp[0]

    return candies


def getConceptSports(word):
    searchTerm = word
    link = 'http://conceptnet.io/c/en/'
    link = link+searchTerm
    print(link)
    http_pool = url.connection_from_url(link)
    r = http_pool.urlopen('GET', link)
    http_pool.close()
    html = r.data.decode('utf-8')
    soup = b(html, features="html5lib")

    divs = soup.findAll("a")
    termsWithContext = []
    derivedTerms = []
    tWC = []
    dT = []
    contextCandies = []
    derivedCandies = []

    for d in divs:
        if d.contents[0] == 'Derived terms':
            div = d.find_parent().find_parent()

            if len(div) > 0:
                dinks = div.findAll("a")

                for k in dinks:
                    derivedTerms.append(n.word_tokenize(k.contents[0]))

                del (derivedTerms[0])

                for k in derivedTerms:
                    if len(k) == 1 and not '➜' == k[0] and not k[0] == 'v' and not k[0] == 'n':
                        dT.append(k[0])

                    elif len(k) > 1 and not k[0] == 'v' and not k[0] == 'n' and not k[0] == 'a' and not 'more' in k[
                            0].lower():
                        temp = ""
                        for l in k:
                            if not l == ',':
                                temp = temp + " " + l
                        dT.append(temp[1:])

                derivedCandies = dT

        elif d.contents[0] == 'Terms with this context':
            withContext = d.find_parent().find_parent()

            if len(withContext) > 0:
                links = withContext.findAll("a")
                for k in links:
                    termsWithContext.append(n.word_tokenize(k.contents[0]))

                del (termsWithContext[0])

                for k in termsWithContext:
                    if len(k) == 1 and not '➜' == k[0] and not k[0] == 'v' and not k[0] == 'n':
                        tWC.append(k[0])

                    elif len(k) > 1 and not k[0] == 'v' and not k[0] == 'n' and not k[0] == 'a' and not 'more' in k[0].lower():
                        temp = ""
                        for l in k:
                            if not l == ',':
                                temp = temp + " " + l
                        tWC.append(temp[1:])

                termsWithContext = tWC

                for i in range(len(termsWithContext)):

                    if " " in termsWithContext[i]:
                        termsWithContext[i] = termsWithContext[i].replace(" ", "_")
                    elif "-" in termsWithContext[i]:
                        termsWithContext[i] = termsWithContext[i].replace("-", "_")

                    link = 'http://conceptnet.io/c/en/' + termsWithContext[i]
                    http_pool = url.connection_from_url(link)
                    r = http_pool.urlopen('GET', link)
                    htm = r.data.decode('utf-8')
                    http_pool.close()
                    s = b(htm, features="html5lib")

                    fibs = s.findAll("a")

                    for j in fibs:
                        if j.contents[0] == 'Context of this term':
                            lin = j.find_parent().find_parent()

                            if len(lin) > 0:

                                ls = lin.findAll("a")
                                pre = []
                                for k in range(len(ls)):
                                    term = n.word_tokenize(ls[k].contents[0])

                                    if len(term) == 1 and not '➜' == term[0] and not term[0] == 'v' and not term[0] == 'n':
                                        pre.append(term[0])

                                    elif len(term) > 1 and not term[0] == 'v' and not term[0] == 'n' and not term[0] == 'a' and not 'more' in \
                                        term[0].lower():
                                        temp = ""
                                        for l in term:
                                            if not l == ',':
                                                temp = temp + " " + l
                                        pre.append(temp[1:])
                                del(pre[0])
                                pre = list(set(pre))

                                if searchTerm in pre and len(pre) < 3:
                                    if "_" in termsWithContext[i]:
                                        temp = termsWithContext[i]
                                        temp = temp.replace("_", " ")
                                        contextCandies.append(temp)
                                    else:
                                        contextCandies.append(termsWithContext[i])

            contextCandies = list(set(contextCandies))
            c = []
            for i in contextCandies:
                if not searchTerm in i:
                    c.append(i)
            contextCandies = c

    if len(contextCandies) > 1:
        return contextCandies
    else:
        return derivedCandies


def getSentiWordNetRating(word):
    f = open("SentiWordNet_3.0.0.txt", "r")
    for x in f:
        if word + '#' in x:
            x = x.split("\t")
            # print(x)
            negRating = float(x[3])
            if negRating < 0.25:
                return True
            else:
                return False


def getSentiWordNetWords(word, candidates):
    f = open("SentiWordNet_3.0.0.txt", "r")
    c = []
    for x in f:
        if ' ' + word + ' ' in x:
            x = x.split("\t")
            x[len(x) - 2] = x[len(x) - 2].split("#")[0]

            if word in x[len(x) - 1]:

                if len(x[len(x) - 2].split(" ")) > 1:

                    for j in x[len(x) - 2].split(" "):

                        if "_" in j:
                            j = j.replace("_", " ")
                        if j not in candidates:
                            c.append(j)
                else:
                    if "_" in x[len(x) - 2]:
                        temp = x[len(x) - 2].replace("_", " ")
                        if temp not in candidates:
                            c.append(temp)
                    elif not x[len(x) - 2] == word and x[len(x) - 2] not in candidates:
                        c.append(x[len(x) - 2])

    return c


def wordInSentiNet(word):
    f = open("SentiWordNet_3.0.0.txt", "r")
    for x in f:
        if ' ' + word + ' ' in x:
            x = x.split("\t")
            split = x[len(x) - 2].split("#")
            for i in split:
                if word in i:
                    return True
            compare = x[len(x) - 2].split("#")[0]
            if word == compare or word in compare:
                return True
    return False


def filter(list):
    c = []
    for k in list:
        if not n.pos_tag(n.word_tokenize(k))[0][1] == 'JJ' \
                and not n.pos_tag(n.word_tokenize(k))[0][1] == 'RB' \
                and not k[0:4] == 'anti' \
                and not k[0:3] == 'non':
            c.append(k)

    return c


def capitalize(word):
    nick = ""

    sp = (word.split(" "))
    if len(sp) > 1:
        for k in range(len(sp)):
            if not sp[k] == '':
                f = sp[k][0]
                rest = sp[k][1:]
                if k == len(sp)-1:
                    nick = nick + (f.upper() + rest)
                elif k < len(sp):
                    nick = nick + (f.upper() + rest) + " "

    else:
        f = word[0]
        rest = word[1:]
        nick = f.upper() + rest

    return nick


def normalize(list):
    tagged = []
    for i in range(len(list)):
        first = list[i][0].lower()
        second = list[i][1]
        tagged.append((first, second))
    return tagged


def getRhymes(word):
    r = []
    for i in range(len(word)):
        if len(word[i:]) > 1:
            t = p.rhymes(word[i:].lower())
            temp = []
            if len(t) > 0:
                r.append(temp)

    u = []
    for k in range(len(r) - 1):
        u = set(u).union(set(r[k]).union(set(r[k + 1])))
    return list(u)


def lastResort(word):
    r = []
    for i in range(len(word)):
        if len(word[i:]) > 1:
            t = findWordNetRhymes(word[i:].lower())
            temp = []
            for j in t:
                if wordInSentiNet(j) and len(j) > 2:
                    temp.append(j)
            if len(temp) > 0:
                r.append(temp)
    u = []
    for k in range(len(r) - 1):
        u = set(u).union(set(r[k]).union(set(r[k + 1])))
    return list(u)


def findWordNetRhymes(word):
    w = d(word.lower())[0]

    res = []
    for ss in wn.words():
        if d(ss)[0] == w:
            res.append(ss)

    if len(res) < 1:
        word = word[1:]
        if len(word) > 1:
            print("Going one level further")
            return findWordNetRhymes(word)
    else:
        return res


def getWikiSports():
    links = ['https://en.wikipedia.org/wiki/list_of_sports', "https://www.topendsports.com/events/summer/sports/index.htm",
             "https://en.wikipedia.org/wiki/List_of_hobbies"]
    answer = ""
    for i in links:
        http_pool = url.connection_from_url(i)
        r = http_pool.urlopen('GET', i)
        html = r.data.decode('utf-8')
        http_pool.close()
        soup = b(html, features='html.parser')
        answer = answer + "\n" + str(soup).lower()

    return answer


def getMovieGenres():
    genres = {"action": "https://www.filmsite.org/actionfilms4.html",
              "adventure": "https://www.filmsite.org/adventurefilms4.html",
              "animated": "https://www.filmsite.org/animatedfilms7.html",
              "biopic": "https://www.filmsite.org/biopics2.html",
              "comedy": "https://www.filmsite.org/comedyfilms7.html",
              ("crime", "gangster"): "https://www.filmsite.org/crimefilms4.html",
              "cult": "https://www.filmsite.org/cultfilms4.html",
              "drama": "https://www.filmsite.org/dramafilms3.html",
              "melodrama": "https://www.filmsite.org/melodramafilms4.html",
              ("epic", "historical", "period"): "https://www.filmsite.org/epicsfilms3.html",
              "fantasy": "https://www.filmsite.org/fantasyfilms3.html",
              ("film-noir", "noir", "filmnoir"): "https://www.filmsite.org/filmnoir6.html",
              ("detective", "mystery"): "https://www.filmsite.org/mysteryfilms3.html",
              "horror": "https://www.filmsite.org/horrorfilms5.html",
              "supernatural": "https://www.filmsite.org/supernatfilms2.html",
              ("musicals", "musical", "dance", "dances"): "https://www.filmsite.org/musicalfilms7.html",
              "romance": "https://www.filmsite.org/romancefilms5.html",
              ("scifi", "sci-fi", "science-fiction"): "https://www.filmsite.org/sci-fifilms7.html",
              ("superhero", "superheroes", "heros", "heroes"): ["https://www.filmsite.org/superheroesonfilm12.html",
                                                                "https://www.filmsite.org/superheroesonfilm13.html",
                                                                "https://www.filmsite.org/superheroesonfilm14.html"],
              ("thriller", "suspense"): "https://www.filmsite.org/thrillerfilms4.html",
              "war": "https://www.filmsite.org/warfilms6.html",
              ("western", "westerns"): "https://www.filmsite.org/westernfilms6.html",
              "silent": "https://www.filmsite.org/silentfilms2.html"}
    answer = ""
    keys = genres.keys()
    for i in keys:
        if isinstance(i, tuple):
            for j in i:
                answer = answer + " " + j
        else:
            answer = answer + " " + i
    return answer


def rhyme(word):
    word = word.lower()
    r = p.rhymes(word)
    results = []

    if len(r) < 3:
        print('starting wordnet rhymes')
        t = findWordNetRhymes(word)
        print('finished wordnet rhymes')

        if len(t) > 0:
            for i in range(len(t)):
                if "-" in t[i]:
                    t[i] = t[i].replace("-", " ")
                elif "_" in t[i]:
                    t[i] = t[i].replace("_", " ")

            r = list(set(r + t))

    if len(r) < 3:
        print('starting get rhymes')
        r = list(set(r + getRhymes(word)))
        print('finished get rhymes')

    print(r)
    for i in r:
        if getSentiWordNetRating(i):
            results.append(i)

    global rhymingNames
    rhymingNames = results


def getMovieNicknames(word, firstName):
    word = word.lower()
    movies = []
    results = []

    if word == "gangster" or word == "gang":
        word = "crime"
    elif word == "historical" or word == "period":
        word = "epic"
    elif word == "film-noir" or word == "filmnoir":
        word = "noir"
    elif word == "detective":
        word = "mystery"
    elif word == "musicals" or word == "dance":
        word = "musical"
    elif word == "sci-fi" or word == "science-fiction":
        word = "scifi"
    elif word == "westerns":
        word = "western"
    elif word == "suspense":
        word = "thriller"
    elif word == "superhero" or word == "superheroes" or word == "heroes":
        word = "hero"
    elif word == "romantic":
        word = "romance"
    elif word == "funny":
        word = "comedy"
    elif word == "biopic":
        word = "documentary"

    link = "www.google.com/search?q=best+" + word + "+movies"
    http_pool = url.connection_from_url(link)
    r = http_pool.urlopen('GET', link)
    http_pool.close()
    html = r.data.decode('latin-1')
    soup = b(html, 'html.parser')
    # print(soup)

    for div in soup.findAll('div', class_='BNeawe s3v9rd AP7Wnd'):
        if not '.' in div.contents[0] and not '<' in div.contents[0] and len(div.contents[0]) > 1:
            # print(div.contents[0])
            movies.append(div.contents[0])
            # print(len(div.contents[0]))
        # if not div.descendants == None:
        #     for i in div.descendants:
        #         try:
        #             if '<' in str(i) and i.has_attr('class'):
        #                 print(i)
        #         except AttributeError:
        #             pass

                    # if i.has_attr('class') and div['class'] == ['BNeawe s3v9rd AP7Wnd']: print(i)

    for a in soup.findAll("a"):
        # print(a)
        # print()
        # if a.has_attr('class') and a['class'] == ['BVG0Nb']: print(a)
        if a.has_attr('class') and a['class'] == ['EDblX DAVP1']:
            if "q=" in a['href']:
                text = a['href']
                text = text.split("q=")[1]
                text = text.split("stick=")[0]
                text = text.replace("+", " ")
                text = text.replace("&", " ")
                text = text.replace("%", " ")
                text = text.replace("(film)", " ")
                text = text.replace("(film)", " ")

                if 3 < len(text.split(" ")) < 6:
                    c = 0
                    temp = ""
                    for i in text.split(" "):
                        if i == "C3" or i == "A7" or i == "A8" or i == "E2" or i == "80":
                            c += 10
                        if i == "":
                            c += 1
                        if not i.isdigit():
                            temp = temp + i + " "
                    if c < 2:
                        temp = temp[:-1]
                        movies.append(temp)

    for i in movies:
        done = False
        if len(i) > 1:
            res = n.pos_tag(n.word_tokenize(i))
            if len(res) > 2:
                s = ""
                for j in res:
                    if j[1] == "NNP" and not done:
                        s = s + firstName + " "
                        done = True
                    else:
                        s = s + j[0] + " "
                if firstName in s:
                    results.append(s[:-1])

    return results


def question1(text):
    if len(text) > 0:
        text = text.split(" ")
        t = []
        for i in text:
            if not i == "":
                t.append(i)
        text = t
        if len(text) > 0:
            length = len(text)
            global firstName
            global middleName
            global lastName

            if length == 3:
                cap1 = text[0][0].upper()
                cap2 = text[1][0].upper()
                cap3 = text[2][0].upper()
                firstName = cap1 + text[0][1:]
                middleName = cap2 + text[1][1:]
                lastName = cap3 + text[2][1:]
                thread = threading.Thread(target=rhyme, args=(firstName,))
                thread.start()

            elif length == 2:
                cap1 = text[0][0].upper()
                cap2 = text[1][0].upper()
                firstName = cap1 + text[0][1:]
                lastName = cap2 + text[1][1:]
                thread = threading.Thread(target=rhyme, args=(firstName,))
                thread.start()

            elif length == 1:
                cap1 = text[0][0].upper()
                firstName = cap1 + text[0][1:]
                thread = threading.Thread(target=rhyme, args=(firstName,))
                thread.start()
            return True
        else:
            return False
    else:
        return False


def question2(m):
    sportsCandidates = []
    sports = getWikiSports()
    tagged = []
    m = m.lower()
    print("User entered sport: ", m)

    if "no" in m or "none" in m or "not really" in m or "nope" in m:
        return -1

    m = n.word_tokenize(m)
    temp = normalize(n.pos_tag(m))
    sNouns = nounGetter(temp)
    sVerbs = verbGetter(temp)

    # print(sports)
    for i in sNouns:
        if i in sports:
            tagged.append(i)

    for i in sVerbs:
        if i in sports:
            tagged.append(i)

    if len(tagged) < 1:
        return []

    for i in tagged:
        c = getConceptTermsWithContext(i)
        for h in c:
            global firstName
            s = h + " " + firstName
            sportsCandidates.append(s)

    return sportsCandidates


def question3(m):
    terms = []

    m = m.lower()

    if "no " in m or "none " in m or "not really " in m or "nope " in m:
        return -1

    m = n.word_tokenize(m)
    for i in m:
        test = " " + i.lower() + " "
        if test in movieGenres:
            terms.append(i)
    results = []

    global firstName
    for i in terms:
        r = getMovieNicknames(i, firstName)
        for j in r:
            temp = j.split(" ")
            if len(temp) > 2:
                if " & amp ; " in j:
                    j = j.replace(" & amp ; ", " & ")
                    results.append(j)
                else:
                    results.append(j)


    return results


def giveNickname(boolean, m):

    print("Generating Rhyming Nickname")
    m = m.lower()

    global rhymingNames
    global personal

    while isinstance(rhymingNames, int):
        time.sleep(2)

    if boolean or len(rhymingNames) < 1:
        personal = True
        if "sport" in m:
            nickname = random.choice(sportsNames)
            return "\"" + capitalize(nickname) + "\""
        elif "movie" in m:
            nickname = random.choice(movieNames)
            return"\"" + capitalize(nickname) + "\""


    else:
        personal = False
        nickname = random.choice(rhymingNames)
        nickname = "\"" + capitalize(nickname) + " " + firstName + "\""
        return nickname


def writeToJSON(dict, file):
    try:
        with open(file) as f:
            data = json.load(f)
    except json.decoder.JSONDecodeError:
        data = {}

    data.update(dict)

    with open(file, 'w') as f:
        json.dump(data, f)


def getIndexFromJson(file):
    with open(file) as f:
        data = json.load(f)

    keys = list(data.keys())
    if len(keys) > 0:
        return int(keys[-1])
    else:
        return -1


def personalChoice(file):
    with open(file) as f:
        data = json.load(f)

    keys = list(data.keys())
    pers = 0
    nonpers = 0

    if len(keys) > 0:
        for i in keys:
            if data[i]["personal"]:
                pers += 1
            else:
                nonpers += 1

    if pers > nonpers:
        print("Personal count: " + str(pers))
        print("Non-personal count: " + str(nonpers))
        # print(False)
        return False
    elif pers < nonpers:
        print("Personal count: " + str(pers))
        print("Non-personal count: " + str(nonpers))
        # print(True)
        return True
    else:
        choice = random.choice([0, 1])
        if choice == 0:
            print("Personal count: " + str(pers))
            print("Non-personal count: " + str(nonpers))
            # print(True)
            return True
        else:
            print("Personal count: " + str(pers))
            print("Non-personal count: " + str(nonpers))
            # print(False)
            return False


def printBalance(file):
    with open(file) as f:
        data = json.load(f)

    keys = list(data.keys())
    pers = 0
    nonpers = 0

    if len(keys) > 0:
        for i in keys:
            if data[i]["personal"]:
                pers += 1
            else:
                nonpers += 1

    print("Personal tests: " + str(pers))
    print("Non-personal tests: " + str(nonpers))


printBalance("data.json")

def smallTalk(index):
    eel.changeHTML(smalltalkies[index])
    global smalltalk

    if index == len(smalltalkies)-1:
        smalltalk = True
    else:
        smalltalk = False
    return smalltalkies[index]


#%% Program
movieGenres = getMovieGenres()

eel.init('web')
message = "base"


@eel.expose
def py_send(n):
    eel.send(n)(print_result)

@eel.expose
def print_result(n):
    global message
    message = n


eel.start('main2.html', size=(500, 800), block=False)


global personal
personal = personalChoice("data.json")
personal = True
print("Personal Nickname is: " + str(personal))

index = 0
currentQuestion = ""
running = True

sportsNames = []
movieNames = []
sportsAnswer = ""
movieAnswer = ""

while running:
    eel.sleep(1)
    if not message == "base" and len(message) > 1:
        if message == "ready" and not qs[0]:
            eel.changeHTML(qtexts[0])
            currentQuestion = qtexts[0]
            message = "base"
        elif not qs[0]:
            if question1(message):
                qs[0] = True
                eel.changeHTML(smalltalkies[index])
                currentQuestion = smalltalkies[index]
                index += 1
                message = "base"
            else:
                message = "base"
                eel.changeHTML("I am sorry, what was your name?")
                currentQuestion = "I am sorry, what was your name?"

        elif not smalltalk:
            smallTalk(index)
            currentQuestion = smallTalk(index)
            index += 1
            message = "base"
        elif not qs[1]:
            sportsNames = question2(message)
            print(sportsNames)
            if isinstance(sportsNames, list):
                if len(sportsNames) > 1:
                    qs[1] = True
                    sportsAnswer = message
                    message = "base"
                    eel.changeHTML(qtexts[3])
                    currentQuestion = qtexts[3]
                else:
                    eel.changeHTML(qtexts[2])
                    currentQuestion = qtexts[2]
                    message = "base"
            elif sportsNames == -1:
                eel.changeHTML("Alright but if you had to pick a sport, which would it be?")
                currentQuestion = "Alright but if you had to pick a sport, which would it be?"
                message = "base"

        elif not qs[2]:
            movieNames = question3(message)
            print(movieNames)
            if isinstance(movieNames, list):
                if len(movieNames) > 1:
                    qs[2] = True
                    movieAnswer = message
                    message = "base"
                    eel.changeHTML(qtexts[5])
                    currentQuestion = qtexts[5]
                else:
                    eel.changeHTML(qtexts[4])
                    currentQuestion = qtexts[4]
                    message = "base"
            elif movieNames == -1:
                eel.changeHTML("Alright but if you had to pick a genre, which would it be?")
                currentQuestion = "Alright but if you had to pick a genre, which would it be?"
                message = "base"

        elif not qs[3]:
            # print(personal)
            final = giveNickname(personal, message)
            print(final)
            eel.changeHTML("I like the nickname " + str(final) + ". I think I'm going to call you that from now on. \n \n"
                                                            "Well I've got some computer-related stuff to get to so I'll catch you later, "
                                                            + str(final) + "!")
            eel.removeHTML()
            qs[3] = True

            index = getIndexFromJson("data.json") + 1
            # print("Index from JSON; " + str(index - 1) + " Current index: " + str(index))
            data = {index: {"participantName": firstName,
                            "personal": personal,
                            "nickname": str(final),
                            "sportsAnswer:": sportsAnswer,
                            "movieAnswer:": movieAnswer,
                            "sports": sportsNames,
                            "movies": movieNames,
                            "rhymes": rhymingNames
                            }}
            writeToJSON(data, "data.json")
            message = "base"
            running = False
            printBalance('data.json')
    elif len(message) < 1:
        # print("here")
        eel.changeHTML("Sorry I didn't get that. " + currentQuestion)
        message = "base"












