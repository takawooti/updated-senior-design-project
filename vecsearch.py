#!/usr/bin/env python3

import argparse
import chromadb
from chromadb.config import Settings
from termcolor import colored
import json
import string

def run():
    #Creates the command line argument parser and handles the "index" and "search" commands
    parser = argparse.ArgumentParser(
                    prog='vecsearch.py',
                    description='Perform a vector-based document search',
                    epilog='Thanks for using!')
    parser.add_argument('command', help='Enter the word "search" or "index" based on desired use')          
    parser.add_argument('vecpath', help='Path for the vectorized database')      
    parser.add_argument('-d', '--datapath', help='Path to the data directory')
    parser.add_argument('-q', '--query', help='Desired search query string')
    parser.add_argument('--numterms', type=int, default=5,help='Number of most relevant terms within a result document to display')
    parser.add_argument('--maxdocs', type=int, default=10, help='For index: Maximum number of documents to process. For search: Maximum number of result documents to display')
    args = parser.parse_args()
    if args.command == "index":
        index(args.datapath, args.vecpath, args.maxdocs)
    elif args.command == "search":
        search(args.query, args.vecpath, args.maxdocs, args.numterms)
    
def search(query, vecpath, maxdocs, numterms):
    #Queries the collection "docs" for the most relevant documents to the search query
    client = chromadb.PersistentClient(path=vecpath)
    collection = client.get_or_create_collection(name="docs")
    results = collection.query(query_texts = query, n_results = maxdocs, include=['metadatas','documents', 'distances'])
    ids = results.get('ids')[0]
    metadatas = results.get('metadatas')[0]
    distances = results.get('distances')[0]
    documents = results.get('documents')[0] 
    print("Results: ")
    order = 1
    terms = set()
    
    if numterms != 0:
        #Creates a collection of unique terms from the result documents and queries it to find the most relevant terms to the search query
        for d in documents:
            tokens = tokenize(d)
            terms.update(tokens)
        
        client_temp = chromadb.Client() 
        collection_temp = client_temp.get_or_create_collection(name="terms")
        terms = list(terms)
        collection_temp.add(
        documents= terms,
        ids = terms)
        term_results = collection_temp.query(query_texts = query, n_results = len(terms), include=['distances'])
        terms = term_results.get('ids')[0]
        term_distances = term_results.get('distances')[0]
    
    for i,m,d,doc in zip(ids, metadatas, distances, documents):
        #Prints the document ID, title, distance score, and the most relevant terms found in the document
        title = m.get('title')
        order_string = str(order) + ")"
        rounded = round(d,3)
        doc_terms = set(tokenize(doc))
        print(colored(order_string, attrs = ['bold']), colored("ID:", "green", attrs=['bold']), i, colored("Title:", "green", attrs=['bold']), colored(title, attrs=['underline']), colored("Score:","green", attrs=['bold']), rounded)
        print(" ")
        print(colored(" Most relevant terms: ", 'green', attrs=['bold']))
        terms_found = 0
        for term in terms:
            if term in doc_terms:
                print(" " + term)
                terms_found += 1
                if terms_found == numterms:
                    print(" ")
                    break
        order +=1
 
def tokenize(str_var):
    #Removes punctuation, converts to lowercase, and splits the string into tokens
    return str_var.translate(str.maketrans('', '', string.punctuation)).lower().split()
    
#def find_revelant_terms(query, text):
    #Tokenizes the text and query, creates a temporary collection of the tokens, and queries the collection for the most relevant tokens to the query. Will be implemented in future updates
    tokens = list(set(text.lower().split()))
    client = chromadb.Client()
    collection = client.get_or_create_collection(name="tokens")
    collection.add(
    documents= tokens,
    ids = tokens)
    results = collection.query(query_texts = query, n_results = args.numterms, include=['distances'])
    ids = results.get('ids')[0]
    distances = results.get('distances')[0]
    return zip(ids,distances)
 
def index(datapath, vecpath, maxdocs):
    #Checks if the collection "docs" exists, if so it deletes it and creates a new one
    client = chromadb.PersistentClient(path=vecpath, settings = Settings(allow_reset=True))
    
    collections = client.list_collections()
    collection_names = [c.name for c in collections]

    target_collection_name = "docs"
    if target_collection_name in collection_names:
        client.reset()
        #client.delete_collection(name="docs")
    
    collection = client.get_or_create_collection(name="docs")
    with open(datapath, 'r') as f_in:
        batch = []
        #Adding documents to the collection in batches of 20
        for i, line in enumerate(f_in):
            entry = json.loads(line)
            details = {
            'id' : entry.get('id'),
            'title' : entry.get('title'),
            'abstract' : entry.get('abstract')
            }
            batch.append(details)
            if len(batch) == 20:

                documents = []
                metadatas = []
                ids = []
                for details in batch:
                  combine_text = details.get('title') +" " + details.get('abstract')
                  documents.append(combine_text)
                  ids.append(details.get("id"))
                  metadatas.append({"title": details.get("title")})

                collection.add(
                documents= documents,
                metadatas= metadatas,
                ids= ids )
                batch.clear()
            if i > maxdocs:
                print("Done!")
                break
        #Adding any remaining documents in the batch to the collection
        if batch:
            documents = []
            metadatas = []
            ids = []
            for details in batch:
              combine_text = details.get('title') +" " + details.get('abstract')
              documents.append(combine_text)
              ids.append(details.get("id"))
              metadatas.append({"title": details.get("title")})

            collection.add(
            documents= documents,
            metadatas= metadatas,
            ids= ids )
            batch.clear()
            
if __name__ == "__main__":
    run()