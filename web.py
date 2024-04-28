from flask import Flask, render_template, request
from json import load
from time import time

# Load the urls dictionary from JSON
print("Loading sites.json...")
f = open("sites.json", "r")
urls = load(f)
f.close()

# Load the images dictionary from JSON
print("Loading images.json...")
f = open("images.json", "r")
images = load(f)
f.close()

app = Flask(__name__)

@app.route('/')
def index():
    
    query = request.args.get('q', '')
    
    if query == "":
        return render_template('index.html')
    
    start_time = time()
    
    # Get the keywords from the query
    keywords = {}
    for word in query.split(' '):
        real_word = ''.join(c for c in word if c.isalpha())
        if real_word in keywords.keys():
            keywords[real_word] += 1
        else:
            keywords[real_word] = 1

    # Store relevent entries
    results = {}
    for url in urls.keys():
        relevance = 0
        for word in urls[url][2].keys():
            for keyword in keywords.keys():
                if word.lower() == keyword.lower():
                    relevance += urls[url][2][word] * keywords[keyword]
        if relevance > 0:
            results[url] = relevance

    # Sort the results by relevance
    sorted_results = {k: v for k, v in sorted(results.items(), key=lambda item: item[1])}
    
    # Get relavent images
    image_results = []
    for url in reversed(sorted_results.keys()):
        if url in images.keys():
            image_results.append(images[url])
        if len(image_results) >= 10:
            break

    end_time = time()
    
    return render_template("search.html", query = query, urls = urls, results_num = len(results), images = image_results, results = list(reversed(sorted_results))[0:min(49,len(sorted_results))], start_time = start_time, end_time = end_time)


# ...

app.run()