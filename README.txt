This library will provide tools to parse and extract information from bitstreams.

Planned features:
	Parse following files:
		Regular .bit bitstreams
		Raw bitstreams (.bin)
		ASCII raw bitstreams (.rbt)
		Mask files (.msk, .msd)
		Essential Bitfiles (.ebd) (Proprietary. Fuctionality not yet verified. Use at own risk)
		Readback files (.rbb, .rba, .rbd, JCM .data files)
		.ll files (TODO)

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
	FradStructure contains methods for accessing frame data as well as FAR incrementing logic.
	FrameOperations performs useful operations to compare data from two FradStructure objects.
