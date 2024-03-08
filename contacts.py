#!/usr/bin/python3
# -*- coding: utf8 -*-

import vobject
import re

class Telmap(dict):
	'''	A dictionary, loaded from a VCard file and containing a map: normalized phone -> contact name '''

	def __init__(self, fname):
		super(dict, self).__init__()
		with open(fname, encoding='utf8') as f:
			data = f.read()
			cards = vobject.readComponents(data)
			for card in cards:
				name = self.normalize_name(card.fn.value)
				details = []
				if 'org' in card.contents:
					details.extend(card.org.value)
				if 'title' in card.contents:
					details.append(card.title.value)
				details = list(filter(lambda x: x, details))
				if details:
					name = '{0} ({1})'.format(name, ', '.join(details))
				tels = card.contents.get('tel')
				if tels:
					for tel in tels:
						self[self.normalize_tel(tel.value)] = name

	@classmethod
	def normalize_tel(self, s):
		s = re.sub('[^0-9]', '', s)
		if len(s) == 6:
			s = '78482' + s
		if s.startswith('8'):
			s = '7' + s[1:]
		return s

	@classmethod
	def normalize_name(self, s):
		s = re.sub('[^\\w\\-\\+\\.]+', ' ', s)
		return s.strip()


if __name__ == '__main__':
	import sys
	import pprint

	# sys.stdout.reconfigure(encoding='utf-8')

	t = Telmap(sys.argv[1])
	pprint.pprint(t)
