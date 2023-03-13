#OPENAI KEY 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
import os
from llama_index import GPTTreeIndex, SimpleDirectoryReader, GPTEmptyIndex


#ddg(keyword, region="us-en") https://pypi.org/project/duckduckgo-search/
from duckduckgo_search import ddg

with open('.apikey.txt') as f:
    key = f.readline()
os.environ['OPENAI_API_KEY'] = key
f.close()
from bs4 import BeautifulSoup
from urllib.request import urlopen

print("skynet 2023")
def search_augment(query):
    #search_context = " "
    #"I just asked you to either search or answer the question, 'where do birds go when it rains', you searched, so here are the results of the search from the first web page, please read them and answer my questions briefly, the results are: " + results
    
    search_idx = query.find("search(")
    if( search_idx != -1):
        search_query = query[query.find("(")+1:query.find(")")] #python be like 
        print("SEARCH AUGMENT! Searching ddg for: " + search_query)
        search_results = ddg(search_query, region="us-en", max_results = 3)
        url = ducks[0]["href"]
        page = urlopen(url)
        html = page.read().decode("utf-8")
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
windex = GPTTreeIndex([])
while(1):    
    question = input(">>> ")
    if(question == "exit"):
        print("exiting") #stupid
        exit()
    query = question + " (if searching the internet would be helpful please respond with 'search(relevant search prompt here)' to recieve the search results as a followup prompt)"
    #fix this asap so u dont waste tokens/$$$ OR DONT 
    #res = index.query("where do birds go when it rains?", mode = "default").response
    res = index.query(query).response
    print("Input response: " + res)
    res = index.query(augments(res))
    print(res.response)


  

    