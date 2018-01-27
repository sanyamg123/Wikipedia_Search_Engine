It is a search-engine that is designed based on **Block sort based indexing** and further uses relevance ranking based on the **tf-idf scores*** of the documents in the Wikipedia Dump.

Install **Pystemmer** which is a Python interface to the stemming algorithms from the Snowball
project (http://snowball.tartarus.org/).

To create the **inverted_index_file** of some **WIKI_XML** dump, Run:  
```python Indexer.py <WIKI_XML_DUMP_FILE_NAME> ```

To **query** in the WIKI dump: ```python query.py```

The **query and output** on my XML dump looks as in the screenshot:

![ScreenShot](https://raw.github.com/sanyamg123/Wikipedia_Search_Engine/master/querypython.png)
