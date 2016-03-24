from FradStructure import FradStructure
import numpy

class EssentialBitParser:
	"""
	This class parses an essential bit file (.ebd) and loads a FradStructure with the data.
	A 1 in an .ebd file indicates an essential bit. File format is ASCII
	"""

	def __init__(self):
		"""
		Construct a new EssentialBitParser object
		:return: returns nothing
		"""

	def parse_file(self, ebdFile, fradStructure):
		"""
		This function parses the specified ebd file and loads a FradStructure object with the data
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
				result = 0
				for i in range(32):
					if line[i] == "1":
						val = 0x080000000 >> i
						result += val
				fradStructure.append_word(result)
				wordCount += 1
			else:
				continue


if __name__ == '__main__':
	from FrameOperations import FrameOperations
	from BitParser import BitParser
	ebd = FradStructure(7)
	ebd.load_frads('./frads/xc7z020_frads.txt')
	ebdParser = EssentialBitParser()
	ebdParser.parse_file("../ECEn493r/ZynqTestFiles/logic.ebd", ebd)

	frads1 = FradStructure(7)
	frads1.load_frads('./frads/xc7z020_frads.txt')
	bitParser1 = BitParser()
	bitParser1.parse_file("../ECEn493r/ZynqTestFiles/logic.bit", frads1)

	frads2 = FradStructure(7)
	frads2.load_frads('./frads/xc7z020_frads.txt')
	bitParser2 = BitParser()
	bitParser2.parse_file("../ECEn493r/ZynqTestFiles/logicWithFaults.bit", frads2)


	frameOps = FrameOperations(frads1, frads2)
	upsets = frameOps.find_essential_upsets(ebd)

	print "Essential Upsets:"
	for upset in upsets:
		print "Frame: " + str(hex(upset[0])) + " Word: " + str(upset[1]) + " Bit: " + str(upset[2])