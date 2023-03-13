
#Dylan Lanigan-Smith's code, don't copy it unless I said you could, or do, can't really stop ya
#testing on python 3.10.9 macOS Ventura mpb m1 
#add an api key file
import os
#greasy way to do this
import logging, sys

logfile = open("llama.log", "w")
logging.basicConfig(stream=logfile, level=logging.INFO)

from llama_index import GPTTreeIndex, SimpleDirectoryReader, GPTEmptyIndex



#ddg(keyword, region="us-en") https://pypi.org/project/duckduckgo-search/
from duckduckgo_search import ddg

with open('.apikey.txt') as f: #FILE IN SAME DIRECTORY AS PROGRAM, FIRST LINE IS API KEY NOTHING ELSE
    key = f.readline()
os.environ['OPENAI_API_KEY'] = key
f.close()
if len(key) < 20:
    print("API KEY IS PROBABLY AN ISSUE") # hashtag never handle exceptions in personal projects 
    exit()

from bs4 import BeautifulSoup
from urllib.request import urlopen, HTTPError, URLError, Request
from socket import timeout

print("skynet 2023")

#issues:
#timeouts/https errors
#doesnt know date 
#...

def search_augment(in_query, query):
    #search_context = " "
    #from test one: "I just asked you to either search or answer the question, 'where do birds go when it rains', you searched, so here are the results of the search from the first web page, please read them and answer my questions briefly, the results are: " + results
    
    search_idx = query.lower().find("search(")
    if( search_idx != -1):
        search_query = query[query.find("(")+1:query.find(")")] #python be like 
        print("SEARCH AUGMENT! Searching ddg for: " + search_query)
        search_results = ddg(search_query, region="us-en", max_results = 3)
        while(len(search_results) < 1):
             search_results = ddg(search_query, region="us-en", max_results = 3)
        url = search_results[0]["href"]
        print("SEARCH AUGMENT! Attempting to scrape:  " + url)
        req = Request(
            url, 
            data=None, 
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )
        try: #TODO make function and have it try next result if failure
            html = urlopen(req, timeout=15).read().decode('utf-8')
        except (HTTPError, URLError) as error:
            print('Data %s not retrieved because %s\nURL: %s', error, url)
            logfile.close() #greasy
            raise "No can do buddy"
        except timeout:
            print('socket timed out - URL %s', url)
            logfile.close()
            raise "sorry bro"
        
        soup = BeautifulSoup(html, "html.parser")
        results = soup.find_all("p") #make better
        content = ""
        for res in results:
            content += res.get_text() + " " #this way is better: https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
        if len(content) > 2048:
            content = content[0 : 2047]
        
        query += " This is the content of the first webpage for search prompt '" + search_query + "' please utilize them to answer from the provided previous context the initial question that prompted you to search. Do not refer to the initial question directly, instead reword it so that your answer works as a statement with the subject of the question included. Do not refer to having searched the web either, just answer the question professionally and with intelligent choice of included details. Make sure to end your answer by suggesting some sources of bias that the webpage you found info from may potentially have. Previous user question for that prompted your search for context: " + in_query + "Results:" + content.strip()
        return query

def augments(in_query, query):
    query = search_augment(in_query, query)
    return query

documents = SimpleDirectoryReader('data').load_data()
index = GPTTreeIndex(documents)
#windex = GPTTreeIndex([])
while(1):    
    question = input(">>> ")
    if(question == "exit"):
        print("exiting") #stupid
        logfile.close()
        exit()
    in_query = question + " (if searching the internet would be helpful please respond with 'search(relevant search prompt here)' to recieve the search results as a followup prompt)" #it is okay to not search
    #fix this asap so u dont waste tokens/$$$ OR DONT 
    #res = index.query("where do birds go when it rains?", mode = "default").response
    res_str = index.query(in_query).response
    print("Input response: " + res_str)
    res =  index.query(augments(in_query, res_str))
    print(res.response)


  
    
