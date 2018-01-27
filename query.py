from collections import *
import sys
from Stemmer import Stemmer as PyStemmer
import os
import heapq
import math
import operator
import string
import time

reload(sys)
sys.setdefaultencoding('utf-8')
ps = PyStemmer('porter')
stopwords = {}
tfidf_file = []
tfidf_file.append(open('./title/final.txt','r'))
tfidf_file.append(open('./text/final.txt','r'))
tfidf_file.append(open('./category/final.txt','r'))
document_titles = open('doc_titles.txt', 'r')
document_titles_offset = []
directory_names = ["title", "text", "category"]
allwords = [defaultdict(int) for i in range(3)]

#defaultdict(int) is just like a vector of vectors
#defaultdict(list) is just like a vector of vectors of vectors  
docs = defaultdict(float)
#this creates just a simple map/vector that can store key value pairs
def offset_of_document_titles():
	rl = document_titles.readlines()
	offset = 0
	for rll in rl:
		document_titles_offset.append(offset)
		offset += len(rll)#one is for '\n' as well

offset_of_document_titles()#call to the above function

#now go for tag file offsets
def tag_file_offsets(tagno):
	os.chdir(directory_names[tagno])
	with open("term_offset.txt") as file:
		lines = file.readlines()
		for word in lines :
			word = word.split(':')
			allwords[tagno][word[0]] = int(word[1].strip())
	file.close()
	os.chdir("../")

#we make offsets for easy retrieval of data from the file
tag_file_offsets(0)
tag_file_offsets(1)
tag_file_offsets(2)

def query_with_tag( word, tagno ):
	if word in allwords[tagno]:
		offset = allwords[tagno][word]
		tfidf_file[tagno].seek(offset)
		line = tfidf_file[tagno].readline()
		line = line.split(' ')
		# print("hello")
		#line[0] now has the word and line[1] now has the tfidf scores
		for word in line[1:len(line)]:
			# print(word+"hello")
			word = word.split('d')
			if len(word) > 1:
				word = word[1].split('c')
				if len(word)>1:
					docs[word[0]] += float(word[1])

def query_without_tag ( word ):
	for i in range(3):
		# print("hello")
		query_with_tag(word,i)

def relevance_ranking ( ):
	sorted_docs = sorted(docs.items(),key = operator.itemgetter(1),reverse= True)
	sorted_docs = sorted_docs[:min(10,len(docs))]
	print(len(sorted_docs))
	for doc in sorted_docs:
		document_titles.seek(document_titles_offset[int(doc[0])])
		line = document_titles.readline().strip()#strip strips off any newline characters at the end
		line = string.replace(line,' ','_')
		print ("https://en.wikipedia.org/wiki/" + line)

c = "y"
print ("Do u want to query ? (y/n) ")
c = raw_input()

while c[0]=='y':
	print (" What is your phrase query ? ")
	words = raw_input().strip('\n').lower()
	clock_start = time.time()
	docs = defaultdict(float)
	#t is for title
	#p is for text
	#c is for category
	words = words.split(' ')
	for word in words:
		if ( ':' in word ):
			word = word.split(':')
			word[1] = ps.stemWord(word[1])
			if ( word[0]=='t' ):
				query_with_tag(word[1],0)
			elif ( word[0]=='p' ):
				query_with_tag(word[1],1)
			elif ( word[0]=='c' ):
				query_with_tag(word[1],2)
			else :
				query_without_tag(word[1])	
		else :
			word = ps.stemWord(word)
			query_without_tag(word)
	relevance_ranking()
	print ("Query time = " +str(time.time()-clock_start))
	print ("Do u want to query ? (y/n) ")
	c = raw_input()

for i in range(3):
	tfidf_file[i].close()









