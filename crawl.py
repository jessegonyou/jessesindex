from os import curdir
from threading import Thread
from time import sleep
from bs4 import BeautifulSoup
from urllib import robotparser
from urllib.request import urlopen, Request
import urllib.error
from json import load, dumps
from sys import exit

url_queue = [input('url to start from : ')]
blocked = ["https://amazon.com", "https://amzn.to", "https://youtube.com", "https://tiktok.com", "https://www.amazon.com", "https://www.amzn.to" "https://www.youtube.com", "https://www.tiktok.com"]

# Load the urls dictionary from JSON
f = open("sites.json", "r")
urls = load(f)
f.close()

kill_threads = False
threads_killed = 0

def crawler(thread_number = 0):

    # GLOBAL VARS TO ACCESS
    global url_queue
    global urls
    global blocked
    global threads_killed

    last_site = ""
    
    while len(url_queue) != 0:
        
        if kill_threads:
            print(f"Terminating thread {thread_number}")
            threads_killed += 1
            break
        
        current_url = url_queue[0]
        del(url_queue[0])
        
        try:    
            
            # TODO: Parse sitemap.xml

            if not (current_url.startswith('http://') or current_url.startswith('https://')):
                continue
            
            # Skip this url if it ends with an unparsable extension
            invalid_ext = False
            for ext in ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'webm', 'ogg', 'mp3', 'mp4', 'wav', 'flac', 'xml']:
                if current_url.endswith('.'+ext) or current_url.endswith('.'+ext+'/'):
                    invalid_ext = True
            if invalid_ext:
                continue

            if not current_url.endswith('/'):
                current_url = current_url + '/'  

            # Seperate the domain name and path of the URL
            domain = current_url[:current_url[current_url.find('://')+3:].find('/')+current_url.find('://')+3]
            path = current_url[current_url.find(domain)+len(domain):]

            # Skip if this URL is blocked
            if domain in blocked:
                print(str(thread_number) + " [ BLOCKED ] " + current_url + " " + str(len(urls)) + " " + str(len(url_queue)))
                continue    

            # Parse robots.txt
            try:
                if not last_site == domain:
                    botparser = robotparser.RobotFileParser()
                    botparser.set_url(domain + '/robots.txt')
                    botparser.read()
                last_site = domain

                # Skip the url if it is denied by robots.txt
                if not botparser.can_fetch("JessesIndex", path):
                    print(str(thread_number) + " [ BLOCKED ] " + current_url + " " + str(len(urls)) + " " + str(len(url_queue)))
                    
                    # If everything is denied by robots.txt, add the website to the block list
                    if not botparser.can_fetch("JessesIndex", "/"):
                        blocked.append(domain)
                    continue
        
            # If a connection error occurs, allow access
            except (urllib.error.HTTPError, urllib.error.URLError):
                pass
            
            # Get the first URL in the queue
            try:
                response = urlopen(Request(current_url, headers = {"User-Agent": f"JessesIndex/1.0 (worker {thread_number})"}))
            except Exception:
                print(str(thread_number) + " [ NO CONN ] " + current_url + " " + str(len(urls)) + " " + str(len(url_queue)))
                continue
        
            # Parse the html response
            soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
        
            # Add every link to the queue
            for link in soup.find_all('a'):
                link_url = link.get('href')
                if type(link_url) != str:
                    continue
                link_url = link_url.split('#')[0].split('?')[0]
                if not ( link_url in urls.keys() or link_url in url_queue ):
                    url_queue.append(link_url)
                    
            if not ( domain in urls.keys() or domain in url_queue ):
                url_queue.append(domain)    
                
            # Add every keyword to a dictionary
            keywords = {}
            page_text = soup.get_text()
            page_words = page_text.split()
            for word in page_words:
                real_word = ''.join(c for c in word.lower() if c in "abcdefghijklmnopqrstuvwxyz")
                if real_word == '':
                    continue
                if real_word in keywords.keys():
                    keywords[real_word] += 1 / len(page_words)
                else:
                    keywords[real_word] = 1 / len(page_words)
            
            print(str(thread_number) + " [ CRAWLED ] " + current_url + " " + str(len(urls)) + " " + str(len(url_queue)))
            
            # Get page_text into a state where it can easily be displayed
            page_text = page_text.replace("\n"," ").strip()
            while "  " in page_text:
                page_text = page_text.replace("  ", " ")

            # Store these statistics in a new entry in the dictionary
            urls[current_url] = [soup.title.string if soup.title.string != "" else current_url, page_text[0:min(500, len(page_text))] if page_text[0:min(500, len(page_text))] != "" else "This site does not have a description", keywords]
        
        except KeyboardInterrupt:
            raise
        
        except:
            print(str(thread_number) + " [  ERROR  ] " + current_url + " " + str(len(urls)) + " " + str(len(url_queue)))
            continue

# Create a few workers
print('Spooling up')
threads = []
for x in range(5):
    threads.append(Thread(target=crawler, args=[x]))
    threads[-1].start()
    sleep(5)

print('Done creating workers.')

# Wait until program termination
try:
    while 1:
        sleep(5)    
        
except KeyboardInterrupt:
    pass
    
finally:
    
    print('Requesting crawlers terminate')
    kill_threads = True
    
    secs_waited = 0
    while threads_killed < 5:
        sleep(1)
        secs_waited += 1
        if secs_waited >= 60:
            print('Threads have taken too long to terminate. Continuing anyway.')
            break
        
    # Free up some memory
    del(url_queue)
    del(blocked)

    # Dump urls to JSON file
    print('Writing to index')
    f = open("sites.json", "w")
    f.write(dumps(urls))
    f.close()
    
    print("Done!")
    exit()
