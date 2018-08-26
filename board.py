import string
import random
init_points = {"AEIOULNSTR":1, "DG":2, "BCMP": 3, "FHVWY":4, "K":5, "JX":8, "QZ":10}
initString = "AAAAAAAAABBCCDDDDEEEEEEEEEEEEFFGGGHHIIIIIIIIIJKLLLLMMNNNNNNOOOOOOOOPPQRRRRRRSSSSTTTTTTUUUUVVWWXYYZ~~"

class Tile:
	def __init__(self, letter):
		self.let = letter
		val = 0	
		for key in init_points:
			if self.let in key:
				val = init_points[key]
		self.val = val
	def update(self, letter):
		self.let = letter
		for key in init_points:
			if self.let in key:
				self.val = init_points[key]
	def letter(self):
		return self.let
	def value(self):
		return self.val
	def __eq__(self, other):
		return self.letter() == other.letter()
	def __repr__(self):
		return self.letter()
	def __str__(self):
		return self.letter()
	def is_letter(self):
		return self.letter().upper() in initString


class Multiplier:
	def __init__(self, amount, word=False):
		self.word = word
		self.amount = amount
	def getAmount(self):
		return self.amount
	def notWord(self):
		return not self.word

class TileBag:
	def __init__(self):
		self.freqs = list(initString)
	def dec(self,tile):
		self.freqs.remove(tile.letter())
	def numTiles(self):
		return len(self.freqs)
	def gen(self, n):
		allLetters = []
		for i in range(n):
			let = self.freqs[random.randint(0, self.numTiles() - 1)]
			allLetters.append(Tile(let))
			self.dec(Tile(let))
		return allLetters


class Board:
	def __init__(self):
		self.grid = [[Tile("1 ") for i in range(15)] for k in range(15)]
		self.muls = [[Multiplier(1) for i in range(15)] for k in range(15)]
		self.scores = [0, 0]
		self.turn = 0
		self.bag = TileBag()
		self.playerTiles = [self.bag.gen(7), self.bag.gen(7)]
		self.empty = True
	def getGrid(self):
		return self.grid
	def display(self):
		for y in range(15):
			for x in range(15):
				if (self.grid[y][x].isLetter()):
					print(self.grid[y][x].letter() + "  "),
				else:
					print(self.grid[y][x].letter() + " "),
			print("\n")
	def force(self, x, y, letter):
		if x not in range(15) or y not in range(15):
			print("Not valid location")
			return
		self.grid[y][x] = Tile(letter.upper())
	def setMul(self, x, y, amount, word=False):
		self.muls[y][x] = Multiplier(amount, word)
		txt = str(amount)
		if word:
			txt += "w"
		else:
			txt += " "
		self.grid[y][x] = Tile(txt)

	#Accept tiles as [x,y, Tile]
	def check(self,tiles):
		xBin= []
		yBin = []
		for item in tiles:
			xBin.append(item[0])
			yBin.append(item[1])
		sets = [set(xBin), set(yBin)]
		vert = 0
		okay = True
		gaps = []
		k = 0
		if len(sets[0]) > 1 and len(sets[1]) > 1:
			print("not linear")
			okay = False
			return (None, 0)

		if len(sets[1]) > 1:
			vert = 1
		bins = [xBin, yBin]
		var = bins[vert]
		if (len(var) != len(sets[vert])):
			print("no duplicates allowed")
			return (None, 0)
		full = list(range(min(var),max(var)+1))
		for item in var:
			full.remove(item)
		for item in full:
			if vert:
				gaps.append([xBin[0], item])
			else:
				gaps.append([item,yBin[0]])
		return (gaps, vert)

	"""Checks to make sure no gaps will exist before placing tiles down"""
	def noGaps(self,tiles):
		gaps = self.check(tiles)[0]
		if gaps is None:
			return False
		for gap in gaps:
			if not self.grid[gap[1]][gap[0]].isLetter():
				return False
		return True


	"""Places tiles after ensuring:
		1) that no tiles already exist there
		2) that the placed tiles border existing ones """
	def place(self,tiles):
		tiles = self.sortTiles(tiles)
		first = False
		tmp = [row[:] for row in self.grid]
		tempTiles = self.playerTiles[self.turn]
		blnk = 0
		if len(tiles) == 1:
			print("One letter words are not valid\n")
			return None
		if self.empty:
			centered = False
			for x,y,letter in tiles:
				if x == 7 and y == 7:
					centered = True
					break
			if not centered:
				print("Please place in middle of board")
				return None
		if not self.noGaps(tiles):
			print("Not proper placement")
			return None
		for x,y,til in tiles:
		 	if til not in tempTiles:
		 		if Tile("~") in tempTiles:
		 			blnk += til.value()
		 			til = Tile("~")
		 		else:
		 			print("\nYou don't have the letter: " + til.letter() + "\n")
		 			return None
		 	tempTiles.remove(til)
		
		neighbors = 0
		for x,y,letter, in tiles:
			if self.grid[y][x].isLetter():
				print("Can't place over existing tile")
				return None
			tmp[y][x] = letter	
		for x, y, letter in tiles:
			neighbors += self.count(tmp,x,y)
		#There must be more neighbors than just the placed tiles
		if neighbors <= 2*(len(tiles)-1) and not first and self.check(tiles)[0] is not None and len(self.check(tiles)[0]) == 0 and not self.empty:
			print("Please place next to adjacent tiles")
			return None
		print("words generated are...  "),
		full = self.allWords(tmp, tiles, self.check(tiles)[1])
		allTiles = [[i[0] for i in q] for q in full]
		noBad = self.checkWords(allTiles)
		if noBad is False:
			print("please try another move.")
			return None
		points = self.findPoints(full) - blnk
		print("This move scored  " + str(points) + " points.")
		self.scores[self.turn] += points
		print("Player " + str(self.turn) + " now has " + str(self.scores[self.turn]) + " points.\n\n")
		for x,y, letter in tiles:
			self.setMul(x,y,1)
		self.playerTiles[self.turn] += self.bag.gen(len(tiles))
		self.turn = 1 - self.turn
		self.grid = [row[:] for row in tmp]
		self.empty = False
		print("It is now player " + str(self.turn) + "'s turn")
		self.display()
		print("Player " + str(self.turn) + "'s tiles are... " + str(self.playerTiles[self.turn]))
		return 0
	def testPlace(self, letters):
		use = []
		for x, y, letter in letters:
			use.append([x, y, Tile(letter)])
		return self.place(use)

	def sortTiles(self, tiles):
		return sorted(sorted(tiles,key=lambda x:x[0]), key=lambda y:y[1])

	"""Counts neighbors of a given location"""
	def count(self, arr, x,y):
		k = 0
		if x < 14 and arr[y][x+1].isLetter():
			k += 1
		if x > 0 and arr[y][x-1].isLetter():
			k += 1
		if y < 14 and arr[y+1][x].isLetter():
			k += 1
		if y > 0 and arr[y-1][x].isLetter():
			k += 1
		return k

	"""Generates all words from the tiles being placed"""
	def allWords(self, gr, tiles, vert):
		words = []
		wrd = []
		ms=[]
		allMuls = []
		if vert == 1:
			for x,y,tile in tiles:
				wrd = []
				ms = []
				while x >= 0 and gr[y][x].isLetter():
					x -= 1
				x += 1
				while x < 	15 and gr[y][x].isLetter():
					wrd.append(gr[y][x])
					ms.append(self.muls[y][x])
					x += 1
				x -= 1
				if len(wrd) > 1:
					words.append(wrd)
					allMuls.append(ms)
			yi = tiles[0][1]
			x = tiles[0][0]
			wrd = []
			ms = []
			while yi >= 0 and gr[yi][x].isLetter():
				yi -= 1
			yi += 1
			while yi < 15 and gr[yi][x].isLetter():
				wrd.append(gr[yi][x])
				ms.append(self.muls[yi][x])
				yi += 1
		else:
			for x,y,tile in tiles:
				wrd = []
				ms = []
				while y >= 0 and gr[y][x].isLetter():
					y -= 1
				y += 1
				while y < 15 and gr[y][x].isLetter():
					wrd.append(gr[y][x])
					ms.append(self.muls[y][x])
					y += 1
				y -= 1
				if len(wrd) > 1:
					words.append(wrd)
					allMuls.append(ms)
			xi = tiles[0][0]
			y = tiles[0][1]
			wrd = []
			ms = []
			while xi >= 0 and gr[y][xi].isLetter():
				xi -= 1

			xi += 1
			while xi < 15 and gr[y][xi].isLetter():
				wrd.append(gr[y][xi])
				ms.append(self.muls[y][xi])
				xi += 1
		if len(wrd) > 1:
			words.append(wrd)
			allMuls.append(ms)
		result = []
		if len(words) != len(allMuls):
			print("Something went wrong")
			return [[]]
		for n in range(len(words)):
			result.append(zip(words[n],allMuls[n]))
		return result

	def testAllWords(self, gr, letters, vert):
		use = []
		for x, y, letter in letters:
			use.append([x,y,Tile(letter)])
		return self.allWords(grid, use, vert)


	def sortTiles(self, tiles):
		return sorted(sorted(tiles,key=lambda x:x[0]), key=lambda y:y[1])


	"""Takes in group of tiles"""
	def convertWords(self, group):
		words = []
		for tiles in group:
			wrd = []
			for tile in tiles:
				wrd.append(tile.letter())
			words.append(''.join(wrd))
			print(''.join(wrd) + "  "),
		print("\n")
		return words

	"""Given group of words in form of [[tile]], verifies if all words exist""" 	
	def checkWords(self, group):
		allGood = True
		words = self.convertWords(group)
		for word in words:
			filename = makeName(word[0])
			all_words =[line.rstrip('\n') for line in open(filename)]
			first = 0
			last = len(all_words)-1
			found = False
			while first <= last:
				mid = (first + last)/2 #Checks using binary search
				if all_words[mid] == word.lower():
					found = True
					break
				elif word.lower() < all_words[mid]:
					last = mid - 1
				else:
					first = mid + 1
			if found is False:
				print(word + " is not a word sorry")
				allGood = False
		return allGood

	"""Given group of words in the form of [[(tile,Multiplier)]], determines the score of the move"""
	def findPoints(self, group):
		score = 0
		for word in group:
			wordMul = 1
			wordTot = 0
			for pair in word:
				if pair[1].notWord():
					wordTot += (pair[0].value() * pair[1].getAmount())
				else:
					wordTot += pair[0].value()
					wordMul *= pair[1].getAmount()
			score += wordTot*wordMul
		return score

	"""Returns score, declares winner, and ends game"""
	def finish(self):
		self.display()
		print("Player 0:  " + str(self.scores[0]))
		print("Player 1:  " + str(self.scores[1]))
		winner = self.scores.index(max(self.scores))
		print("GAME OVER: Player " + str(winner) + " has won.")




"""....Building and Testing Functionality...."""

def createAll():
	for letter in string.ascii_lowercase:
		create(letter)

def create(name):
	thing = makeName(name)
	dictionary = [line.rstrip('\n') for line in open('ospd.txt')]
	target = open(thing, 'w')
	for word in dictionary:
		if word[0] == name:
			target.write(word)
			target.write('\n')
	target.close()
def makeName(char):
	return "ospd/" + char + ".txt"
			
# def test():
# 	z = Board()
# 	z.force(2,2, "C")
# 	z.setMul(3,7,2)
# 	z.setMul(10,10,2)
# 	z.setMul(3,3,2,True)
# 	# z.force(0,3,"S")
# 	if z.getGrid()[2][2].letter() != "C":
# 		print("ERROR: Problem with force")
# 		return
# 	z.testPlace([[2,3,"A"], [2,4,"T"]])
# 	if z.testPlace([[0,3,"S"],[1,3,"T"], [3,3,"Y"]]) is None:
# 		print("ERROR: Should pass crossword layout")
# 		z.display()
# 		return
# 	z.testPlace([[1,4,"A"], [1,5,"X"], [1,6,"E"],[1,7,"S"]])
# 	z.testPlace([[4,3,"S"],[4,4,"A"], [4,5,"Q"], [4,6, "K"]]) 
# 	z.testPlace([[2,7,"U"],[3,7,"N"]])
# 	z.testPlace([[0,4,"O"]])
# 	z.testPlace([[3,8,"O"]])
# 	print("\n\n...............\n")
# 	#z.display()
# 	z.finish()
# 	print("..........\n")
# 	print("All tests pass.")
# 	return z

def start():
	z = Board()
	z.setMul(0,0,3, True)
	z.setMul(7,0,3, True)
	z.setMul(0,7,3, True)
	z.setMul(0,14,3, True)
	z.setMul(14,0,3, True)
	z.setMul(7,14,3, True)
	z.setMul(14,7,3, True)
	z.setMul(14,14,3, True)

	z.setMul(7,7,2, True)
	z.setMul(1,1,2, True)
	z.setMul(2,2,2, True)
	z.setMul(3,3,2, True)
	z.setMul(4,4,2, True)
	z.setMul(10,10,2, True)
	z.setMul(11,11,2, True)
	z.setMul(12,12,2, True)
	z.setMul(13,13,2, True)
	z.setMul(1,13,2, True)
	z.setMul(13,1,2, True)
	z.setMul(12,2,2, True)
	z.setMul(2,12,2, True)
	z.setMul(3,11,2, True)
	z.setMul(11,3,2, True)
	z.setMul(10,4,2, True)
	z.setMul(4,10,2, True)

	z.setMul(1,5,3)
	z.setMul(5,1,3)
	z.setMul(1,9,3)
	z.setMul(9,1,3)
	z.setMul(13,5,3)
	z.setMul(5,13,3)
	z.setMul(9,13,3)
	z.setMul(13,9,3)
	z.setMul(5,5,3)
	z.setMul(5,9,3)
	z.setMul(9,5,3)
	z.setMul(9,9,3)

	z.setMul(0,3,2)
	z.setMul(3,0,2)
	z.setMul(0,11,2)
	z.setMul(11,0,2)
	z.setMul(14,3,2)
	z.setMul(14,11,2)
	z.setMul(11,14,2)
	z.setMul(3,14,2)
	z.setMul(6,6,2)
	z.setMul(6,8,2)
	z.setMul(8,6,2)
	z.setMul(8,8,2)
	z.setMul(2,6,2)
	z.setMul(2,8,2)
	z.setMul(6,2,2)
	z.setMul(8,2,2)
	z.setMul(12,6,2)
	z.setMul(12,8,2)
	z.setMul(6,12,2)
	z.setMul(8,12,2)
	z.setMul(3,7,2)
	z.setMul(7,3,2)
	z.setMul(11,7,2)
	z.setMul(7,11,2)

	z.display()
	print("It is player 0's turn")
	print("Player 0's tiles are... " + str(z.playerTiles[0]))
	return z







