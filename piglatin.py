#Take the users input
words = input("Enter some text to translate into pig latin: ")
print(words)
#Now I need to break apart
words = words.split(' ')
for i in words:
	print(words)
	if len(i) >=4:
		i = i + "%say"%(i[1])
                i = i[2:]
		print(i)
	else:
		pass
