# jessesindex
JessesIndex is a complete python-based search engine and web crawler that I created for a [blog post](https://5ducks.company/post/2024-05-09.html).

To get started, you will need to crawl the web for a bit to fill out the sites.json file. To do this, you can run the following command:
```shell
$ python3 crawl.py
```
It will then prompt you for the site to start crawling from. Just use any random website and let it crawl for a while. When you feel it has done enough, use CTRL+C and wait for the program to quit.

Once the sites.json file is filled with some data, you can start the JessesIndex WebUI with the following command:
```shell
$ python3 web.py
```

Enjoy!
