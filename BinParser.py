from FradStructure import FradStructure

class BinParser:
	"""
	This class parses binary formatted files including:
		Normal bitstream files (.bit)
		.bin files
		Readback files (.rbb)
		Mask files (.msk)
		JCM readback files (.data)
	It loads a FradStructure with the values obtained from the specified file
	"""
	def __init__(self):
		"""
		Construct a new BinParser object
		:return: returns nothing
		"""
		# A type 2 packet specifying a write (or read in some cases) marks the beginning of the frame data
		self.type2WriteMask = 0x50000000
		self.type2ReadMask = 0x48000000

	def parse_data_file(self, dataFile, fradStructure):
		f = open(dataFile, "rb")
		self.extract_frame_data(f, fradStructure, 0, 0, 1, 1)

	def parse_rbb_file(self, rbbFile, fradStructure):


		header_st = 0
		firstByte_st = 1
		secondByte_st = 2
		thirdByte_st = 3
		fourthByte_st = 4

		currentState = header_st

		# Use state machine to find sync word (0xAA995566).
		# Sync word marks the end of the header and the start of actual commands

		f = open(rbbFile, "rb")

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

		# Find type 2 write packet (start of actual configuration frame data)
		while 1:
			bytes = f.read(4)
			word = (ord(bytes[0]) << 24) | (ord(bytes[1]) << 16) | (ord(bytes[2]) << 8) | ord(bytes[3])
			if (word & self.type2ReadMask) == self.type2ReadMask:
				break
		
		self.extract_frame_data(f, fradStructure, 0, 1, 1, 0)

	def parse_bin_file(self, binFile, fradStructure):
		"""
		Parsing an bin file is actually exactly the same as parsing a bit file. This is just a wrapper.
		:param binFile: Path to bin file to be parsed
		:param fradStructure: FradStructure object to be loaded
		:return: returns nothing
		"""		
		self.parse_bit_file(binFile, fradStructure)

	def parse_msk_file(self, mskFile, fradStructure):
		"""
		Parsing an msk file is actually exactly the same as parsing a bit file. This is just a wrapper.
		:param mskFile: Path to msk file to be parsed
		:param fradStructure: FradStructure object to be loaded
		:return: returns nothing
		"""
		self.parse_bit_file(mskFile, fradStructure)

	def parse_bit_file(self, bitFile, fradStructure):
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

		# Find type 2 write packet (start of actual configuration frame data)
		while 1:
			bytes = f.read(4)
			word = (ord(bytes[0]) << 24) | (ord(bytes[1]) << 16) | (ord(bytes[2]) << 8) | ord(bytes[3])
			if (word & self.type2WriteMask) == self.type2WriteMask:
				break
		
		self.extract_frame_data(f, fradStructure, 1, 0, 1, 0)

	def extract_frame_data(self, fd, fradStructure, includeBram, padFrame, dummyFrames, swapEndian):
		"""
		This function extracts frame data from a file once the location of configuration data has been found.
		:param fd: File descriptor that is pointing to the start of the configuration data
		:param fradStructure: FradStructure object to be loaded by parsing
		:return: returns nothing
		"""
		if padFrame:
			for i in range(fradStructure.wordsPerFrame):
				bytes = fd.read(4)

		# Parse each 32 bit word and store it in appropriate word/frame location
		prevType = 0
		prevTopBottom = 0
		prevRow = 0
		numFrames = fradStructure.get_num_frads() if includeBram else fradStructure.numLogicFrames
		frameCount = 0
		fradStructure.set_current_frad(0)
		while frameCount < numFrames:
			# Skip dummy frames!
			if (dummyFrames == 1) and (fradStructure.get_type() != prevType or fradStructure.get_top_bottom() != prevTopBottom or fradStructure.get_row() != prevRow):
				prevType = fradStructure.get_type()
				prevTopBottom = fradStructure.get_top_bottom()
				prevRow = fradStructure.get_row()
				# 2 dummy frames when type, row, or topBottom boundaries crossed
				for i in range(2*fradStructure.wordsPerFrame):
					bytes = fd.read(4)
			wordCount = 0
			while wordCount < fradStructure.wordsPerFrame:
				bytes = fd.read(4)
				if swapEndian == 0:
					word = (ord(bytes[0]) << 24) | (ord(bytes[1]) << 16) | (ord(bytes[2]) << 8) | ord(bytes[3])
				else:
					word = (ord(bytes[3]) << 24) | (ord(bytes[2]) << 16) | (ord(bytes[1]) << 8) | ord(bytes[0])
				fradStructure.append_word(word)
				wordCount += 1
			frameCount += 1
			fradStructure.step_forward()
		fd.close()		

if __name__ == '__main__':
	from FrameOperations import FrameOperations 
	frads1 = FradStructure(7)
	frads1.load_frads('./frads/xc7k325t_frads.txt')
	bitParser = BinParser()
	bitParser.parse_data_file('../ECEn493r/7SeriesTestFiles/pb_top_newest.data', frads1)

	frads2 = FradStructure(7)
	frads2.load_frads('./frads/xc7k325t_frads.txt')
	bitParser.parse_rbb_file('../ECEn493r/7SeriesTestFiles/pb_top.rbb', frads2)

	frameOps = FrameOperations(frads1, frads2)
	upsets = frameOps.diff(0)

	print "Diff results:"
	for upset in upsets:
		print "Frame: " + str(hex(upset[0])) + " Word: " + str(upset[1]) + " Bit: " + str(upset[2])