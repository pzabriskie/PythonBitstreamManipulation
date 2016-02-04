This library will provide tools to parse and extract information from bitstreams.

Planned features:
	Parse following files:
		Regular .bit bitstreams
		Raw bitstreams (no header)
		ASCII raw bitstreams
		Mask files
		Essential Bitfiles
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