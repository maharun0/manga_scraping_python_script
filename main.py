import os
import requests
from tqdm import tqdm
from typing import List
from bs4 import BeautifulSoup

class Chapter:
    def __init__(self, no, title, link):
        self.no = no
        self.title = title
        self.link = link

    def __str__(self):
        return f"no = {self.no}\ntitle = {self.title}\nlink = {self.link}\n"

def downloadImage(link, imagePath):
    r = requests.get(link)

    with open(imagePath, 'wb') as file:
        file.write(r.content)

def printSoupInFile(soup, location):
    with open(location, "w", encoding='utf-8') as file:
        for content in soup:
            file.write(str(soup) + "\n")

soup = None

def getChapters(url : str) -> List[Chapter]:
    global soup
    tags = soup.find('div', class_="page-content-listing single-page").find_all('a', href=True)
    tags.reverse()
    # printSoupInFile(tags, "tags.html")

    chapters : List[Chapter] = []
    for tag in tags:
        link = tag['href']
        chapter_text = link.split('/')[-2] # chapter-14
        no = chapter_text.split('-')[-1] # 14

        chapter = Chapter(no, f"Chapter {no}", link)
        chapters.append(chapter)
    
    return chapters

def getChapterImageLinks(url) -> List[str]:
    r = requests.get(url)
    chapterSoup = BeautifulSoup(r.content, 'html.parser')
    tags = chapterSoup.find('div', class_='reading-content').find_all('img')

    links : List[str] = []
    for tag in tags:
        links.append(tag['src'][7:])

    return links

def downloadCoverPhoto(dir, url: str) -> None:
    try:
        mangaName = url.split('/')[-2]

        global soup
        coverTag = soup.find_all('img', alt=f"{mangaName}")
        # printSoupInFile(coverTag, f"coverTags.html")

        link = coverTag[0]['src']
        extension = link.split('.')[-1]
        coverPath = f"{dir}/cover.{extension}"

        downloadImage(link, coverPath)
    except:
        print("Couldn't download cover image")

def downloadImagesInFolder(chapter : Chapter, chapterDir) -> None:
    imageLinks : List[str] = getChapterImageLinks(chapter.link)
    # print(*imageLinks, sep='\n')

    # for imageLink in imageLinks:
    for imageLink in tqdm(imageLinks, desc=f"Downloading chapter {chapter.no}"):
        imageName = imageLink.split('/')[-1]

        imagePath = f"{chapterDir}/{imageName}"
        downloadImage(imageLink, imagePath)

def downloadChapters(chapters : List[Chapter], dir):
    for chapter in chapters:
        chapterDir = f"{dir}/chapter_{chapter.no}"

        if os.path.exists(chapterDir):
            continue

        os.mkdir(chapterDir)
        downloadImagesInFolder(chapter, chapterDir)

        print(f"Downloaded Chapter {chapter.no}")

def main():
    # url = "https://1st-kissmanga.net/manga/famous-restaurant/"
    url = input("Enter manga URL: ")

    r = requests.get(url)
    global soup
    soup = BeautifulSoup(r.content, 'html.parser')
    # printSoupInFile(soup, "soup.html")

    # extract manga name
    mangaName = " ".join(word.title() for word in url.split('/')[4].split('-'))

    # make main manga directory
    dir = f"{mangaName}"
    os.makedirs(dir, exist_ok=True)

    # download cover photo
    downloadCoverPhoto(dir, url)

    # make .nomedia file
    nomediaPath = f"{dir}/.nomedia"

    if not os.path.exists(nomediaPath):
        with open(f"{dir}/.nomedia", 'w') as file:
            pass

    # extract chapters
    chapters = getChapters(url)

    # download chapters
    downloadChapters(chapters, dir)
    

main()