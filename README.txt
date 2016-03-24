This library will provide tools to parse and extract information from bitstreams.

Planned features:
	Parse following files:
		Regular .bit bitstreams
		Raw bitstreams (no header)
		ASCII raw bitstreams
		Mask files
		Essential Bitfiles
			Note: ASCII format and only configuration frames, no BRAM
		Readback files
		.ll files

	Ability to query bitstreams on a frame, word, or bit level

	Frame Address Register object/class
		Incrementing, parsing, and indexing
		Support all devices for V5, V6, V7, UltraScale, and UltraScale+ families

	Utilities for comparing and evaluating bits
		Compare frame
		Mask frames
		Extract bits and frames

Class Structure:
	Parser classes will return a fradStructure object after parsing the file given to it.
	fradStructure contains methods for accessing frame data as well as FAR incrementing logic.
	frameOperations performs useful operations to compare data from two fradStructure objects.
