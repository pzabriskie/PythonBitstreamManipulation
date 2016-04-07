from FradStructure import FradStructure
import numpy

class AsciiParser:
	"""
	This class parses ASCII formatted files including:
		.rbt files
		Essential bit files (.ebd)
		Mask files (.msd)
		Readback files (.rbd, .rba)
	It loads a FradStructure with the values obtained from the specified file
	"""

	def __init__(self):
		"""
		Construct a new EssentialBitParser object
		:return: returns nothing
		"""
		# A type 2 packet specifying a write (or read in some cases) marks the beginning of the frame data
		self.type2WriteMask = 0x50000000
		self.type2ReadMask = 0x48000000

	def parse_rbd_file(self, rbdFile, fradStructure):
		"""
		Parses an rbd file and loads a FradStructure object with the data. An rbd file has pad frame and dummy frames but no commands.
		:param rbdFile: Path to rba file to be parsed
		:param fradStructure: FradStructure object to be loaded
		:return: returns nothing
		"""		
		lines = open(rbdFile, 'r').read().split('\n')
		fradStructure.set_current_frad(0)
		frameCount = 0
		wordCount = 0
		padFlag = 0
		dummyFlag = 0
		dummyWordCount = 0
		foundSyncWord = 0
		storeWords = 0
		prevType = 0
		prevTopBottom = 0
		prevRow = 0
		for line in lines:
			if (len(line) > 0 and line[0] == "0") or (line[0] == "1"):
				if (storeWords):
					if(dummyFlag):
						# skip over 202 dummy words at row, topBottom, or type boundaries
						dummyWordCount += 1
						if dummyWordCount == 202:
							dummyFlag = 0
							dummyWordCount = 0
							prevType = fradStructure.get_type()
							prevTopBottom = fradStructure.get_top_bottom()
							prevRow = fradStructure.get_row()
						continue
					if (len(line) > 0):
						result = self.ascii_to_int(line)
						fradStructure.append_word(result)
						wordCount += 1
						if wordCount == fradStructure.wordsPerFrame:
							wordCount = 0
							frameCount += 1
							if(frameCount == fradStructure.numFrads):
								break
							fradStructure.step_forward()
							if(fradStructure.get_type() != prevType or fradStructure.get_top_bottom() != prevTopBottom or fradStructure.get_row() != prevRow):
								dummyFlag = 1
				#clear a frame of pad words
				else:
					wordCount += 1
					if(wordCount == fradStructure.wordsPerFrame):
						wordCount = 0
						storeWords = 1
	def parse_rba_file(self, rbaFile, fradStructure):
		"""
		Parses an rba file and loads a FradStructure object with the data. An rba file has pad frame and dummy frames
		:param rbaFile: Path to rba file to be parsed
		:param fradStructure: FradStructure object to be loaded
		:return: returns nothing
		"""
		lines = open(rbaFile, 'r').read().split('\n')
		fradStructure.set_current_frad(0)
		frameCount = 0
		wordCount = 0
		padFlag = 0
		dummyFlag = 0
		dummyWordCount = 0
		foundSyncWord = 0
		storeWords = 0
		prevType = 0
		prevTopBottom = 0
		prevRow = 0
		for line in lines:
			if (storeWords):
				if(dummyFlag):
					# skip over 202 dummy words at row, topBottom, or type boundaries
					dummyWordCount += 1
					if dummyWordCount == 202:
						dummyFlag = 0
						dummyWordCount = 0
						prevType = fradStructure.get_type()
						prevTopBottom = fradStructure.get_top_bottom()
						prevRow = fradStructure.get_row()
					continue
				if (len(line) > 0):
					result = self.ascii_to_int(line)
					fradStructure.append_word(result)
					wordCount += 1
					if wordCount == fradStructure.wordsPerFrame:
						wordCount = 0
						frameCount += 1
						if(frameCount == fradStructure.numFrads):
							break
						fradStructure.step_forward()
						if(fradStructure.get_type() != prevType or fradStructure.get_top_bottom() != prevTopBottom or fradStructure.get_row() != prevRow):
							dummyFlag = 1
			elif (foundSyncWord == 0):
				if (len(line) > 0 and ((line[0] == "0") or (line[0] == "1"))):
					result = self.ascii_to_int(line)
					if(result == 0xAA995566):
						foundSyncWord = 1
						continue
				else:
					continue
			elif padFlag:
				wordCount += 1
				if(wordCount == fradStructure.wordsPerFrame):
					wordCount = 0
					padFlag = 0
					storeWords = 1
			elif len(line) > 0:
				result = self.ascii_to_int(line)
				if (result & self.type2ReadMask) == self.type2ReadMask:
					padFlag = 1
					continue

	def parse_msd_file(self, msdFile, fradStructure):
		"""
		Parses an msd file and loads a FradStructure object with the data. An msd file has a pad frame and dummy frames.
		Same operation as parsing an rbd file.
		:param msdFile: Path to msd file to be parsed
		:param fradStructure: FradStructure object to be loaded
		:return: returns nothing
		"""
		self.parse_rbd_file(msdFile, fradStructure)	

	def parse_rbt_file(self, rbtFile, fradStructure):
		"""
		Parses an rbt file and loads a FradStructure object with the data. An rbt file is just an ASCII bit file (has dummy frames, no pad frame)
		:param rbtFile: Path to rbt file to be parsed
		:param fradStructure: FradStructure object to be loaded
		:return: returns nothing
		"""
		lines = open(rbtFile, 'r').read().split('\n')
		fradStructure.set_current_frad(0)
		frameCount = 0
		wordCount = 0
		dummyFlag = 0
		dummyWordCount = 0
		foundSyncWord = 0
		storeWords = 0
		prevType = 0
		prevTopBottom = 0
		prevRow = 0
		for line in lines:
			if (storeWords):
				if(dummyFlag):
					# skip over 202 dummy words at row, topBottom, or type boundaries
					dummyWordCount += 1
					if dummyWordCount == 202:
						dummyFlag = 0
						dummyWordCount = 0
						prevType = fradStructure.get_type()
						prevTopBottom = fradStructure.get_top_bottom()
						prevRow = fradStructure.get_row()
					continue
				if (len(line) > 0):
					result = self.ascii_to_int(line)
					fradStructure.append_word(result)
					wordCount += 1
					if wordCount == fradStructure.wordsPerFrame:
						wordCount = 0
						frameCount += 1
						if(frameCount == fradStructure.numFrads):
							break
						fradStructure.step_forward()
						if(fradStructure.get_type() != prevType or fradStructure.get_top_bottom() != prevTopBottom or fradStructure.get_row() != prevRow):
							dummyFlag = 1
			elif (foundSyncWord == 0):
				if (len(line) > 0 and ((line[0] == "0") or (line[0] == "1"))):
					result = self.ascii_to_int(line)
					if(result == 0xAA995566):
						foundSyncWord = 1
						continue
				else:
					continue
			elif len(line) > 0:
				result = self.ascii_to_int(line)
				if (result & self.type2WriteMask) == self.type2WriteMask:
					storeWords = 1
					continue

	def parse_ebd_file(self, ebdFile, fradStructure):
		"""
		This function parses the specified ebd file and loads a FradStructure object with the data.
		The ebd file is still somewhat mysterious and proprietary. No BRAM is included but there are far more bits than the configuration memory holds.
		:param ebdFile: Path to .ebd file to be parsed
		:param fradStructure: FradStructure object to be loaded
		:return: returns nothing
		"""
		lines = open(ebdFile, 'r').read().split('\n')
		fradStructure.set_current_frad(0)
		wordCount = 0
		for line in lines:
			if(wordCount == fradStructure.wordsPerFrame):
				wordCount = 0
				fradStructure.step_forward()
			if (len(line) > 0 and ((line[0] == "0") or (line[0] == "1"))):
				result = self.ascii_to_int(line)
				fradStructure.append_word(result)
				wordCount += 1
			else:
				continue

	def ascii_to_int(self, line):
		"""
		This is a function that takes a line of 32 ascii 1's and 0's to make an integer
		:param line: Line of 32 ascii characters to be converted
		:return: Integer representation of ascii line
		"""
		result = 0
		for i in range(32):
			if line[i] == "1":
				val = 0x080000000 >> i
				result += val
		return result


if __name__ == '__main__':
	from FrameOperations import FrameOperations
	from BinParser import BinParser

	frads1 = FradStructure(7)
	frads1.load_frads('./frads/xc7k325t_frads.txt')
	bitParser1 = BinParser()
	bitParser1.parse_msk_file("../ECEn493r/7SeriesTestFiles/pb_top.msk", frads1)

	frads2 = FradStructure(7)
	frads2.load_frads('./frads/xc7k325t_frads.txt')
	asciiParser = AsciiParser()
	asciiParser.parse_msd_file("../ECEn493r/7SeriesTestFiles/pb_top.msd", frads2)

	frameOps = FrameOperations(frads1, frads2)

	upsets = frameOps.diff(1)

	print "Differences:"
	for upset in upsets:
		print "Frame: " + str(hex(upset[0])) + " Word: " + str(upset[1]) + " Bit: " + str(upset[2])	