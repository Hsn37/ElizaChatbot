from random import randint

def readPair(s):
	colon = s.index(':')
	k = s[:colon]
	v = s[colon+2:]

	return (k,v)

class Keywords():
	def __init__(self, data):
		self.keyword, self.priority, self.decompositions = data

class ELIZA():

	def __init__(self):
		
		self.initial, self.final, self.quit, self.synon, self.pre, self.post, self.keys = self.parseScript()
		self.lastUsedReasmb = {}
		# {(keyword, decomp):reasmb}

		self.active = True

	def parseScript(self):

		f = open('script.txt', 'r')

		init, final, quit, synon = [],[],[],[]
		pre, post = {}, {}
		keys = {}
		stop = False

		lines = f.readlines()
		f.close()

		for i in range(len(lines)):
			key, val = readPair(lines[i].strip())
			# print(val)

			if key == 'pre':
				firstWord = val.split(' ', 1)[0]
				replacement = val.split(' ', 1)[1]
				pre[firstWord] = replacement
			elif key == 'post':
				firstWord = val.split(' ', 1)[0]
				replacement = val.split(' ', 1)[1]
				post[firstWord] = replacement
			elif key == 'initial':
				init.append(val)
			elif key == 'synon':
				synon.append(val)
			elif key == 'quit':
				quit.append(val)
			elif key == 'final':
				final.append(val)
			elif key == 'key':
				keyword = val.split(' ')[0]
				priority = 1
				try:
					priority = int(val.split(' ')[1])
				except:
					pass

				decomp = {}
				i += 1
				key, val = readPair(lines[i].strip())
				
				while True:	
					if key == 'decomp':
						currentDecomp = val
						decomp[currentDecomp] = []

						while True:
							if (i + 1 == len(lines)):
								break

							i += 1
							key, val = readPair(lines[i].strip())

							if key == 'reasmb':
								decomp[currentDecomp].append(val)
							else:
								break
					else:
						# create the key object
						newKey = Keywords((keyword, priority, decomp))
						keys[keyword] = newKey
						break

			if stop:
				break

		return init, final, quit, synon, pre, post, keys

	def startConvo(self):
		return self.initial[randint(0, len(self.initial) - 1)]

	def getAResponse(self, inp):

		inp = inp.lower()
		if inp in self.quit:
			self.active = False
			return self.final[randint(0, len(self.final) - 1)]

		# split and make pre substitutions
		pieces = inp.split(' ')
		self.replacePreSubs(pieces)
		inp = ' '.join(pieces)

		# find keywords and sort them accroding to priority
		keywords = []
		for x in pieces:
			if x in self.keys.keys():
				keywords.append(x)

		keywords.sort(key=lambda x: self.keys[x].priority, reverse=True)

		# choose a reassembly for response based on the keywords and their decompositions
		while True:
			response = self.reassemble(keywords, inp, pieces)
		
			if response[:4] == 'goto':
				keywords = [response[5:]]
			else:
				return response

	def replacePreSubs(self, pieces):
		for i in range(len(pieces)):
			if pieces[i] in self.pre.keys():
				pieces[i] = self.pre[pieces[i]]

	def reassemble(self, keywords, inp, pieces):
		
		for k in keywords:
			key = self.keys[k]

			for decomp, rlist in key.decompositions.items():
				if decomp == '*':
					index = self.chooseReassembly((k, decomp), len(rlist))
					return self.compileFinalResponse(rlist[index], decomp, inp, pieces)
				else:
					if self.checkDecomposition(decomp, inp, pieces):
						index = self.chooseReassembly((k, decomp), len(rlist))
						return self.compileFinalResponse(rlist[index], decomp, inp, pieces)
					else:
						continue

		return self.reassemble(['xnone'], inp, pieces)

	def checkDecomposition(self, decomp, inp, pieces):

		# all possible sentences using synonyms if any. otherwise will be just one sentence
		# splitting over * and white space
		decompSentences = []
		a = decomp.split('*')
		b = []
		for x in a:
			b += x.split(' ')

		# contains only words in the decomp, after removing spaces and *
		c = [x for x in b if x not in ['', ' ']]

		if '@' in decomp:
			synWord = [x[1:] for x in c if '@' in x][0]

			synonyms = []
			for s in self.synon:
				if synWord in s:
					synonyms = s
					break

			ind = c.index('@' + synWord)

			if len(synonyms) > 0:
				for s in synonyms.split(' '):
					l = c.copy()
					l[ind] = s

					if l[0] == '$':
						l.pop(0)
					
					decompSentences.append(l)
		else:
			decompSentences.append(c)


		for sentence in decompSentences:
			cutInput = [z for z in pieces if z in sentence]
			if (cutInput == sentence):
				return True
		
		return False

	def compileFinalResponse(self, resp, decomp, inp, pieces):
		c = [x for x in resp.split(' ') if '(' in x]

		# extracting the number
		try:
			num = int(c[0][1])
		except:
			return resp

		# print(num)
		# print('d', decomp)
		postSentence = ''
		
		p = pieces.copy()
		a = decomp.split(' ')
		
		# print(a)
		# parses the input and cuts according to the decomposition to match sections
		patternedCuts = []
		replacedSyn = ''
		notAStar = True
		for i in range(len(a)):
			if '*' in a[i]:
				patternedCuts.append('*')
				notAStar = False
				if i == len(a) - 1:
					patternedCuts.append(' '.join(p))
				else:
					continue

			elif '@' in a[i]:
				# print('ai', a[i])
				# print(notAStar)
				synWord = a[i][1:]
				synonyms = []
				for s in self.synon:
					if synWord in s:
						synonyms = s
						break

				for l in synonyms.split(' '):
					if l in p:
						replacedSyn = l
						a[i] = l
						break

			if notAStar:
				if a[i] == replacedSyn:
					patternedCuts.append('@')
					patternedCuts.append(a[i])
				else:
					patternedCuts[-1] += ' ' + a[i]
				p.pop(p.index(a[i]))
			else:
				finalindex = 0
				partString = []
				for x in range(len(p)):
					if p[x] == a[i]:
						patternedCuts.append(' '.join(partString))
						if a[i] == replacedSyn:
							patternedCuts.append('@')
						patternedCuts.append(p[x])
						finalindex = x
						notAStar = True
						break
					else:
						partString.append(p[x])

				p = p[finalindex + 1:]

		print('cuts:', patternedCuts)

		finalStr = ''
		count = 0
		for j in range(len(patternedCuts)):
			if '*' in patternedCuts[j] or '@' in patternedCuts[j]:
				count += 1
			if count == num:
				finalStr = patternedCuts[j + 1]
				break


		postSentence = self.replacePostSubs(finalStr.split(' '))
		
		ind = resp.index('(')
		finalResponse = resp[:ind] + postSentence + resp[ind+3:]

		return finalResponse

	def replacePostSubs(self, pieces):

		for i in range(len(pieces)):
			if pieces[i] in self.post.keys():
				pieces[i] = self.post[pieces[i]]

		return ' '.join(pieces)

	def chooseReassembly(self, keyAndDecomp, listLength):

		try:
			self.lastUsedReasmb[keyAndDecomp] = (self.lastUsedReasmb[keyAndDecomp] + 1) % listLength
		except:
			self.lastUsedReasmb[keyAndDecomp] = randint(0, listLength - 1)

		return self.lastUsedReasmb[keyAndDecomp]

def exportKeywords(elc):
	keywordslist = [(x.keyword, x.priority) for x in elc.keys.values()]
	keywordslist.sort(key=lambda x: x[1], reverse=True)
	
	with open('keywords.elz', 'w') as f:
		for x in keywordslist:
			f.write(x[0] + ', ' + str(x[1]) + '\n')


if __name__ == '__main__':

	elc = ELIZA()
	# print(elc.getAResponse('i am happy'))
	print('>>> ' + elc.startConvo())
	while elc.active:
		userInput = input('> ')

		print('>>> ' + elc.getAResponse(userInput.strip()))
