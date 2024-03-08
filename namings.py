#!/usr/bin/python3
# -*- coding: utf-8 -*-

import logging
import re
from datetime import datetime

log = logging.getLogger(__name__)


class FormatError(Exception):
	pass

class NamingError(Exception):
	pass


class NamingScheme(object):

	def __init__(self):
		self.raw = None
		self.dt = None
		self.phone = None
		self.name = None			# optional
		self.is_incoming = None		# optional

	def parse(self, fname):
		return self

	def get_file_extension(self):
		raise NotImplementedError()

	def __str__(self):
		return u"{0}('{1}' phone='{2}' name='{3}')".format(self.__class__.__name__, self.dt, self.phone, self.name)


class XiaomiNaming(NamingScheme):

	SAMPLES = [
		u'Вызов@007846201-89(0078462018955)_20230215113029.mp3',
		u'Вызов@Юляшенька Ю(0079397172318)_20231216123836.mp3',
		u'Вызов@0321(0321)_20231113112139.mp3',
		u'Вызов@112(Экстренный номер)_20220428142049.mp3',
	]

	FORMAT = u'^Вызов\@(.+)\((\d+)\)\_(\d{14})\.mp3$'

	def parse(self, fname):
		match = re.match(self.FORMAT, fname, re.IGNORECASE)
		if match:
			self.raw = fname
			self.name, phone, ts = match.groups()
			self.phone = re.sub('^00(\\d{11})', '+\\1', phone)
			ts_match = re.match('(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', ts)
			yyyy, mm, dd, HH, MM, SS = map(int, ts_match.groups())
			self.dt = datetime(yyyy, mm, dd, HH, MM, SS)
		else:
			raise FormatError("Invalid format")
		return self

	def get_file_extension(self):
		return "mp3"


class LGNaming(NamingScheme):

	SAMPLES = [
		u'0d20151122141548p+74993464260.3gp',
		u'0d20151225135616p+7888888888.3gp',
		u'1d20151209155457pnull.3gp',
		u'1d20151208155808p202020.3gp',
	]
	
	FORMAT = u'^(0|1)d(\d{14})p(.+)\.3gp'

	def parse(self, fname):
		match = re.match(self.FORMAT, fname, re.IGNORECASE)
		if match:
			self.raw = fname
			is_outgoing, ts, phone = match.groups()
			self.is_incoming = bool(int(is_outgoing))
			self.phone = None if phone == 'null' else phone
			ts_match = re.match('(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})', ts)
			yyyy, mm, dd, HH, MM, SS = map(int, ts_match.groups())
			self.dt = datetime(yyyy, mm, dd, HH, MM, SS)
		else:
			raise FormatError("Invalid format")
		return self

	def get_file_extension(self):
		return "3gp"



class NamingFactory(object):

	SCHEMES = [ XiaomiNaming, LGNaming ]

	@classmethod
	def parse(self, fname):
		candidates = []
		for cls in self.SCHEMES:
			try:
				candidates.append(cls().parse(fname))
			except FormatError as x:
				pass
		if not candidates:
			raise NamingError(u"Unknown naming scheme: '{}'".format(fname))
		if len(candidates) > 1:
			raise NamingError(u"Several naming schemes match: '{}'".format(fname))
		return candidates[0]


def test():
	for s in XiaomiNaming.SAMPLES + LGNaming.SAMPLES + ['Hi there']:
		n = NamingFactory.parse(s)
		print(u"{}".format(n))


if __name__ == '__main__':
	test()
