__author__ = 'Peter Zabriskie'
from FradStructure import FradStructure

class FrameOperations:
	"""
	This class stores two FradStructure classes and performs various operations to compare them
	"""

	def __init__(self, fradStructure1, fradStructure2):
		self.fradStructure1 = fradStructure1
		self.fradStructure2 = fradStructure2

	def set_frad_structures(self, fradStructure1, fradStructure2):
		"""
		Set the frad structures to be compared in subsequent operations.
		:param fradStructure1: First frad structure to be used in operations.
		:param fradStructure2: Second frad structure to be used in operations.
		:return: returns nothing
		"""
		self.fradStructure1 = fradStructure1
		self.fradStructure2 = fradStructure2	

	def diff(self, includeBram):
		"""
		Report all word differences between two FradStructure objects
		:return: Array containing (frad, word, bit) upset tuples
		"""
		self.fradStructure1.set_current_frad(0)
		self.fradStructure2.set_current_frad(0)

		upsetList = []

		limit = self.fradStructure1.numFrads if (includeBram) else self.fradStructure1.numLogicFrames
		for i in range(limit):
			frame1 = self.fradStructure1.get_current_frame_data()
			frame2 = self.fradStructure2.get_current_frame_data()

			# print "fradStructure1: " + str(hex(self.fradStructure1.get_current_frad()))
			# print "fradStructure2: " + str(hex(self.fradStructure2.get_current_frad()))
			diffList = self.compare_frame(frame1, frame2)

			for pair in diffList:
				upsetList.append((self.fradStructure1.get_current_frad(), pair[0], pair[1]))

			if len(diffList) > 0:
				self.fradStructure1.print_current_frame()
				self.fradStructure2.print_current_frame()

			self.fradStructure1.step_forward()
			self.fradStructure2.step_forward()

		return upsetList

	def diff_ignore_masked(self, includeBram, mskFradStructure):
		"""
		This function finds upsets between two fradStructures and ignores upsets in masked bits.
		:param mskFradStructure: FradStructure object containing mask information
		"""
		self.fradStructure1.set_current_frad(0)
		self.fradStructure2.set_current_frad(0)
		mskFradStructure.set_current_frad(0)

		upsetList = []

		limit = self.fradStructure1.numFrads if (includeBram) else self.fradStructure1.numLogicFrames

		for i in range(limit):
			frame1 = self.fradStructure1.get_current_frame_data()
			frame2 = self.fradStructure2.get_current_frame_data()
			frame3 = mskFradStructure.get_current_frame_data()

			diffList = self.compare_frame(frame1, frame2)

			for pair in diffList:
				if not ((frame3[pair[0]]) & (1 << pair[1])):
					upsetList.append((self.fradStructure1.get_current_frad(), pair[0], pair[1]))

			if len(diffList) > 0:
				self.fradStructure1.print_current_frame()
				self.fradStructure2.print_current_frame()

			self.fradStructure1.step_forward()
			self.fradStructure2.step_forward()
			mskFradStructure.step_forward()

		return upsetList

	def find_essential_upsets(self, ebdFradStructure):
		"""
		This function finds upsets between two fradStructures and then checks to see
		if upset occurred at an essential bit location
		:param ebdFradStructure: FradStructure object containing essential bit information
		:return: Array containing (frad, word, bit) upset tuples
		"""
		self.fradStructure1.set_current_frad(0)
		self.fradStructure2.set_current_frad(0)
		ebdFradStructure.set_current_frad(0)

		upsetList = []

		for i in range(self.fradStructure1.numLogicFrames):
			frame1 = self.fradStructure1.get_current_frame_data()
			frame2 = self.fradStructure2.get_current_frame_data()
			frame3 = ebdFradStructure.get_current_frame_data()

			diffList = self.compare_frame(frame1, frame2)

			for pair in diffList:
				if (frame3[pair[0]]) & (1 << pair[1]):
					upsetList.append((self.fradStructure1.get_current_frad(), pair[0], pair[1]))

			self.fradStructure1.step_forward()
			self.fradStructure2.step_forward()
			ebdFradStructure.step_forward()

		return upsetList


	def compare_frame(self, frame1, frame2):
		"""
		Helper function to compare frames for use in diff functions

		:param frame1: Array of words in frame1
		:param frame2: Array of words in frame2
		:return: Array of (word, bit) tuples where differences are found
		"""
		return_list = []
		for i in range(len(frame1)):
			# print "i: " + str(i)
			if frame1[i] != frame2[i]:
				# print str(hex(frame1[i])) + ", " + str(hex(frame2[i]))
				for j in range(32):
					msk = 1 << j
					if(frame1[i] & msk) != (frame2[i] & msk):
						return_list.append((i,j))

		return return_list
