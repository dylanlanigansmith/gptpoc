
import os
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
from urllib.request import urlopen, HTTPError, URLError
from socket import timeout

print("skynet 2023")
def search_augment(query):
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
        try: #TODO make function and have it try next result if failure
            html = urlopen(url, timeout=15).read().decode('utf-8')
        except (HTTPError, URLError) as error:
            print('Data %s not retrieved because %s\nURL: %s', error, url)
            raise "No can do buddy"
        except timeout:
            print('socket timed out - URL %s', url)
            raise "sorry bro"
        
        soup = BeautifulSoup(html, "html.parser")
        results = soup.find_all("p") #make better
        content = ""
        for res in results:
            content += res.get_text() + " " #this way is better: https://stackoverflow.com/questions/1936466/how-to-scrape-only-visible-webpage-text-with-beautifulsoup
        query += " This is the content of the first webpage for search prompt '" + search_query + "' please utilize them to answer from the provided previous context the initial question that prompted you to search. Results:" + content
        return query

def augments(query):
    query = search_augment(query)
    return query

documents = SimpleDirectoryReader('data').load_data()
index = GPTTreeIndex(documents)
#windex = GPTTreeIndex([])
while(1):    
    question = input(">>> ")
    if(question == "exit"):
        print("exiting") #stupid
        exit()
    in_query = question + " (if searching the internet would be helpful please respond with 'search(relevant search prompt here)' to recieve the search results as a followup prompt)"
    #fix this asap so u dont waste tokens/$$$ OR DONT 
    #res = index.query("where do birds go when it rains?", mode = "default").response
    res_str = index.query(in_query).response
    print("Input response: " + res_str)
    res = index.query(augments(res_str))
    print(res.response)


  

    
