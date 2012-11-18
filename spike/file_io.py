import codecs
fo = codecs.open("chinese_words.txt", 'r', 'gb18030')
print "file name: ", fo.name
attriStr = fo.readline()
print attriStr
lineStr = fo.readline()
print lineStr
fo.close()