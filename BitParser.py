from FradStructure import FradStructure
from struct import *

class BitParser:
	"""
	This class parses normal bitstream files (.bit) and loads a FradStructure with the values
	"""
	def __init__(self, series):
		"""
		Construct a new BitParser object

		:param series: Series of device related to bitstream
		:return: returns nothing
		"""

		self.series = series
		# A type 2 packet specifying a write marks the beginning of the frame data
		self.type2WriteMask = 0x50000000

		if(series == 5):
			self.wordsPerFrame = 41
		elif(series == 6):
			self.wordsPerFrame = 81
		elif(series == 7):
			self.wordsPerFrame = 101
		elif(series == 8):
			self.wordsPerFrame = 123
		elif(series == 9):
			self.wordsPerFrame = 93

	def parse_file(self, bitFile, fradStructure):
		"""
		This function parses the given bitfile and loads the provided fradStructure with the values
		:param bitFile: Path to bitfile to be parsed
		:param fradStructure: FradStructure object which will store frame data
		:return: returns nothing
		"""

		header_st = 0
		firstByte_st = 1
		secondByte_st = 2
		thirdByte_st = 3
		fourthByte_st = 4

		currentState = header_st

		# Use state machine to find sync word (0xAA995566).
		# Sync word marks the end of the header and the start of actual commands

		f = open(bitFile, "rb")

		while currentState != fourthByte_st:
			byte = f.read(1)
			if currentState == header_st and ord(byte) == 0xAA:
				currentState = firstByte_st
			elif currentState == firstByte_st and ord(byte) == 0x99:
				currentState = secondByte_st
			elif currentState == secondByte_st and ord(byte) == 0x55:
				currentState = thirdByte_st
			elif currentState == thirdByte_st and ord(byte) == 0x66:
				currentState = fourthByte_st								
			else:
				currentState = header_st

		print("Sync word found!\n")

		# Find type 2 write packet (start of actual configuration frame data)
		while 1:
			word = f.read(4)
			if (unpack('I', word) & self.type2WriteMask) == self.type2WriteMask:
				break

		print("Found type 2 write packet!\n")
		


if __name__ == '__main__':
	frads = FradStructure(8)
	frads.load_frads('./frads/xcku040_frads.txt')
	parser = BitParser(8)
	parser.parse_file('../ECEn493r/bitfiles/ff_rb_100_1024_600.bit', frads)

	