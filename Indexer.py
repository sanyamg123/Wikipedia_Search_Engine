#indexer for XML data
from __future__ import print_function
import xml.etree.ElementTree as ET
import re
from collections import *
import sys
from Stemmer import Stemmer as PyStemmer
import os
import heapq
import math

reload(sys)
sys.setdefaultencoding('utf-8')
ps = PyStemmer('porter')
stopwords = {}
XMLLOC = sys.argv[1]
print (XMLLOC)
wordsdict = {}
tags = {'title': 0, 'text': 1, 'category': 2}
cnt = [defaultdict(int) for i in range(3)]
DOC = [defaultdict(list) for i in range(3)]
directory_names = ["title", "text", "category"]
directory_path = ['t','p','c']
total_doc = 0
list_of_digits = ['0','1','2','3','4','5','6','7','8','9']
offset_pointer = []
offset_value = [0,0,0,0]
document_titles = open('doc_titles.txt', 'wb')
posting_pointer = []
file_index = [ 0 ]* 4


def category_wiki_update ( text ):
	regularex = re.findall("\[\[Category:(.*?)\]\]", text)
	if regularex :
		for word in regularex : 
			word = word.split(' ')#list of words in category
			for fword in word : 
				fword = fword.lower()
				fword = ps.stemWord(fword)
				if (fword) and (fword not in stopwords):
					cnt[2][fword] +=1
					wordsdict[fword]=1

def rem_tags_update (text ,which_tag):
	for word in re.split('[^A-Za-z0-9]', text):
		word = word.lower()
		word = ps.stemWord(word)
		if ( word ) and ( word not in stopwords ):
			cnt[tags[which_tag]][word]+=1
			wordsdict[word]=1

def writeintofile( tagno, path, which_words ):
	data = []
	for key in sorted(which_words):
		app = str(key) +' '
		temp = which_words[key]
		if len(temp) > 0:
			idf = math.log10(float(total_doc)/float(len(temp)))
		for i in range(len(temp)):
			s1 = temp[i].split('d')
			if ( len(s1) > 1):
				s2 = s1[1].split('c')
				if ( (len(s2)>1) and (len(s2[1])>0) and (s2[1][0] in list_of_digits) ):#CHECK FOR BUG
					D,C = s2[0],float(s2[1])
					tfidf = (1+math.log10(C))*idf
					tfidf = ("%.2f" % tfidf )
					app += 'd'+ str(D) + 'c' + str(tfidf) + ' '
		data.append(app)
		filename = path+ '/term_offset.txt'
		offset_pointer[tagno].write(key + ':' + str(offset_value[tagno]) + "\n")
		offset_value[tagno] += 1 + len(app)

	posting_pointer[tagno].write('\n'.join(data))
	posting_pointer[tagno].write('\n')




def mergeFiles(tagno , path, total , filetag ):
	listofWords,indexFile,topofFile = {},{},{}
	flag = [0]*total
	data = defaultdict(list)
	heap = []
	countFinalFile = 0
	for i in xrange(total):
		filename = path + filetag + str(i)
		indexFile[i] = open (filename,'rb')
		flag[i] = 1
		topofFile[i] = indexFile[i].readline().strip()
		listofWords[i] = topofFile[i].split(':')
		if listofWords[i][0] not in heap : 
			heapq.heappush(heap,listofWords[i][0])
	count = 0
	while any(flag) == 1 :
		temp = heapq.heappop(heap)
		count +=1 
		for i in xrange(total):
			if ( flag[i] ):
				if listofWords[i][0] == temp:
					data[temp].extend(listofWords[i][1:])
					topofFile[i] = indexFile[i].readline().strip()
					if topofFile[i]=='':
						flag[i] = 0
						indexFile[i].close()
						os.remove(path+filetag+str(i))
					else :
						listofWords[i]=topofFile[i].split(':')
						if listofWords[i][0] not in heap:
							heapq.heappush(heap,listofWords[i][0])
		if count == 100000:
			print("100000exceeded")
			writeintofile(tagno,path,data)
			data = defaultdict(list)
			count = 0
	if count > 0 : 
		writeintofile(tagno,path,data)
		data = defaultdict(list)
				 
with open('stopwords.txt','r') as file :#reading the stopwords (words to be ignored)
	words = file.read().split('\n')#putting the stopwords into a list "words"
	for x in words:
		x = ps.stemWord(x)#stem the stopwords
		stopwords[x]=1

doccnt = 0	
docno = 0	
for event,element in ET.iterparse(XMLLOC,events=("start","end")):
	chop = element.tag
	idx = chop.rfind("}")#it is a namespace actually, and we use namespaces because for eg if we have a field ID both in
	#as well as teacher class then we use a namespace like a link in XML. But we need the end portion after that namespace
	if idx != -1 :
		chop = chop[idx+1:]
	if chop == 'page' and event == 'end':
		#this is the code for a particular page
		for w in wordsdict :
			for t in tags : 
				if cnt[tags[t]][w] > 0 :
					strin = 'd' + str(docno) + 'c' + str(cnt[tags[t]][w])
					DOC[tags[t]][w].append(strin)
		doccnt+=1
		docno +=1
		total_doc += 1
		cnt = [defaultdict(int) for i in range(3)]
		wordsdict = {}
		element.clear()#reason of using iterparse so that we use less portion of the RAM
	elif (chop in tags) and (event == 'end'):
		if chop == "text" :# we will update the category over here by using regular expression in Python
			category_wiki_update(str(element.text))
		rem_tags_update(str(element.text),chop)
		if chop == "title":
			document_titles.write(str(element.text) + '\n') 
	#here is the code for a file that comprises of 2000 pages.
	f_name = ""
	if doccnt >= 2000 :
		doccnt = 0
		for i in range ( 3 ):
			directory = directory_names[i]
			if not os.path.exists(str("./" + directory)):
				os.makedirs(str("./" + directory))
			os.chdir(str("./" + directory))
			s = str(directory_path[i])+str(file_index[i])
			f_name = s
			print ( "created" + f_name )
			f = open(s,"w")
			file_index[i]+=1
			for v in sorted(DOC[i]):
				s = v + ":r"
				for u in DOC[i][v]:
					s += u + ":"	
				print(s,file=f)
			f.close()
			os.chdir('../')
		DOC = [defaultdict(list) for i in range(3)]
		# break#RUN AFTER COMMENTING THIS TO RUN ON THE COMPLETE DATASET


#since the number of documents may not be a multiple of 2000 so I need to write one more if statement like above
if doccnt > 0 :
	doccnt = 0
	for i in range ( 3 ):
		directory = directory_names[i]
		if not os.path.exists(str("./" + directory)):
			os.makedirs(str("./" + directory))
		os.chdir(str("./" + directory))
		s = str(directory_path[i])+str(file_index[i])
		f = open(s,"w")
		file_index[i]+=1
		for v in sorted(DOC[i]):
			s = v + ":"
			for u in DOC[i][v]:
				s += u + ":"
			print(s,file=f)
		f.close()
		os.chdir('../')
	DOC = [defaultdict(int) for i in range(3)]


offset_pointer.append(open("./title/term_offset.txt", 'wb'))
offset_pointer.append(open("./text/term_offset.txt", 'wb'))
offset_pointer.append(open("./category/term_offset.txt", 'wb'))

posting_pointer.append(open("./title/final.txt", 'wb'))
posting_pointer.append(open("./text/final.txt", 'wb'))
posting_pointer.append(open("./category/final.txt", 'wb'))

mergeFiles(0, "./title/", file_index[0], 't')
print("Finalfilecreated"+ str(directory_names[0]))
mergeFiles(1, "./text/", file_index[1], 'p')
print("Finalfilecreated"+ str(directory_names[1]))
mergeFiles(2, "./category/", file_index[2], 'c')
print("Finalfilecreated"+ str(directory_names[2]))

for i in range(3):
	offset_pointer[i].close()
	posting_pointer[i].close()

















