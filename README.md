# updated-senior-design-project
This is a slightly updated version of my Senior Design Project which involved creating a program with a command line user interface that allows the user to perform a vector based document search. It takes the data provided by the user, places it into a vector database, then allows the user to search for a query with their choice of how many results to view along with how close each result is to the query. For each result, the user can choose to see any given number of the most relevant terms within the document that led to the result's closeness score.

I've updated it to rely on the default ChromaDB model. I've also included a basic error check that ensures the user provides arguments as well as some color coding to differentiate between values. I placed a few comments within the code as well to explain what takes place where.

Future improvments I'm looking to make include the ability to add and remove items from the database and providing the user with a choice of embedding model. Currently, each use of the index command creates a new collection to search from.

How to use:
This program requires the installation of ChromaDB and termcolor.

The first thing you'll do is provide the program with the data you'd like to index. I've provided an example JSON to use titled "arxiv-metadata-oai-snapshot-modified.json." The command to do so will look like a variation of the following:

vecsearch.py -d "path\to\json\data\file" --maxdocs (number of documents, default is 10) index "path\to\place\database"

The program will print the word done to signify the collection has been created and all data appended. Now, you ready to perform a search query. The command to do so will be a variation of this:

vecsearch.py -q "Enter your query here" --numterms (number of relevant terms for each result, default is 5) --maxdocs (number of results to show, default is 10) search "path\to\database"

Running vecsearch.py --help also provides a breakdown of each argument and the usage structure.

Thanks for reading!
