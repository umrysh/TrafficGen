#!/usr/bin/python
# -*- coding: utf-8 -*-

#    Built for python 2.7

#    Copyright 2017 Dave Umrysh
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2
import re
import time
import sys
import os
from random import shuffle


try:
	import sqlite3 as lite
except ImportError:
	print("sqlite not installed.")
	sys.exit(1)

try:
	from bs4 import BeautifulSoup
except ImportError:
	print("BeautifulSoup not installed.")
	sys.exit(1)


maxEntries = 500


def main():
	global TheSlash
	global path
	global con
	global cur

	match = re.compile('\.(pdf|mp3)')

	opener = urllib2.build_opener()
	opener.addheaders = [('User-Agent', 'Mozilla/5.0')]

	platform = sys.platform
	if platform.find('win') >= 0:
		TheSlash = '\\'
	else:
		TheSlash = '/'


	path = os.path.expanduser(os.path.join("~",".trafficGen")) + TheSlash
	if not os.path.exists(os.path.expanduser(os.path.join("~",".trafficGen"))):
		os.makedirs(os.path.expanduser(os.path.join("~",".trafficGen")))


	if not os.path.isfile("%strafficGen.db" % path):
		firstTime = True
	else:
		firstTime = False
	con = lite.connect('%strafficGen.db' % path)

	with con:
		con.row_factory = lite.Row
		cur = con.cursor()
		if firstTime:
			# Create all the tables
			print ("Creating the tables...")
			cur.execute("CREATE TABLE websites(url text,UNIQUE(url))")
			cur.execute('insert into websites (url) values("https://umrysh.com")\n')
			con.commit()

		# Start browsing
		while(True):
			# Select the first entry in the table
			cur.execute('Select url,ROWID FROM websites WHERE ROWID IN (SELECT ROWID FROM websites ORDER BY RANDOM() LIMIT 1)')
			row = cur.fetchone()
			url = row["url"]
			rowID = row["ROWID"]

			# Delete this entry from the table
			cur.execute('DELETE FROM websites where ROWID = "%s"\n' % rowID)
			con.commit()

			# GET this entry and grab all urls from the page
			print( "Getting: %s" % url)

			currentCount = 0

			try:
				html_page = opener.open(url)
				soup = BeautifulSoup(html_page, "lxml")
				soupList = soup.findAll('a', attrs={'href': re.compile("^http://")})
				shuffle(soupList)
				for link in soupList:
					# Get the count of how many urls we have
					cur.execute('Select count(*) as total from websites')
					row = cur.fetchone()
					count = row["total"]
					# while we are below our max, add the urls to the table
					if int(count) < maxEntries and not re.search(match, link.get('href')) and currentCount < 10:
						cur.execute('insert OR IGNORE into websites (url) values("%s")\n' % link.get('href'))
						con.commit()
						print ("    Adding: %s" % link.get('href'))
						currentCount = currentCount +1
			except:
				pass

			time.sleep(5) # delays for 5 seconds

if __name__ == "__main__":
	main()