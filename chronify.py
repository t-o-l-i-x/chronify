#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import contacts
import namings
import logging

log = logging.getLogger(__name__)
logging.basicConfig(format = "%(asctime)s %(levelname)s %(message)s", level = logging.DEBUG, stream = sys.stderr)

class Statistics(object):

	def __init__(self):
		self.non_files = 0
		self.naming_errors = 0
		self.processed = 0
		self.failed = 0

	def __str__(self):
		return repr(self.__dict__)


def main():
	stats = Statistics()

	if len(sys.argv) < 4:
		raise Exception("Usage: $0 SOURCES_DIR TARGET_DIR VCARD_FILE")

	src_path = sys.argv[1]
	dst_path = sys.argv[2]
	telmap = contacts.Telmap(sys.argv[3])

	for fname in os.listdir(src_path):
		if not os.path.isfile(os.path.join(src_path, fname)):
			stats.non_files += 1
			continue
		try:
			recording = namings.NamingFactory.parse(fname)
			ts = recording.dt.strftime("%Y-%m-%dT%H-%M-%S")
			phone = telmap.normalize_tel(recording.phone) if recording.phone else ''
			name = telmap.get(phone)
			new_fname = ' '.join(filter(lambda x: x, [ts, phone, name]))
			new_fname += "." + recording.get_file_extension()

			# os.rename(os.path.join(dir, fname), os.path.join(dir, new_fname))
			# os.link(os.path.join(dir, fname), os.path.join(dir, new_fname))

			os.symlink(os.path.join(src_path, fname), os.path.join(dst_path, new_fname))
			stats.processed += 1

		except namings.NamingError as x:
			log.error("Wrong recording name: %s", fname)
			stats.naming_errors += 1
		except:
			log.exception(fname)
			stats.failed += 1

	print(stats)


if __name__ == '__main__':
	main()

