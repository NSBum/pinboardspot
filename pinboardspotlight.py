#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import urllib
import sqlite3
import dateutil.parser
import plistlib
import subprocess
import sys
import os
from pprint import pprint
import argparse
import shlex
import re

parser = argparse.ArgumentParser(description='Pinboard Spotlight Sync')
parser.add_argument('-u','--user',help = 'Pinboard user name', required = True)
parser.add_argument('-p','--password',help = 'Pinboard Password', required = True)
parser.add_argument('-d','--database', help = 'Path to database', required = False)
parser.add_argument('-w','--webloc', help = 'Path to webloc file storage', required = True)
args = vars(parser.parse_args())
pprint(args)

if args['database'] == None:
	args['database'] = os.path.dirname(os.path.abspath(__file__))

url = 'https://%s:%s@api.pinboard.in/v1/posts/all?format=json' % (args['user'].strip(), args['password'].strip())

def sanitizeName(name):
	name = ''.join([i if ord(i) < 128 else '' for i in name])
	name = re.sub("['\"\\.\\/\\\\\\s]+", "_", name)
	name = name.replace('\'','')
	name = name.replace('/','')
	name = name.replace(' ','_')
	name = name.replace('"','')
	name = (name[:30]) if len(name) > 30 else name
	return name.strip()

def sanitizeTags(t):
	return ''.join([i if ord(i) < 128 else '' for i in t]).strip()

try:
	conn = sqlite3.connect(args['database'].strip())
	conn.row_factory = sqlite3.Row
except Exception, e:
	print 'Error: Unable to connec to pinboardsync db.'
	exit()
else:
	print "Connected to db"
finally:
	pass

#	do we have the right table?
tableSQL = "SELECT tbl_name AS tableName FROM sqlite_master WHERE type='table'"
cursor = conn.cursor()
found = False
cursor.execute(tableSQL)
for row in cursor.fetchall():
	if row["tableName"] == 'pins':
		found = True

if found != True:
	print '''WARN | no pins table exists. Will create.'''
	createTableSQL = '''CREATE TABLE "pins" ("hash" TEXT PRIMARY KEY, "href" TEXT, "date" INTEGER, "tags" TEXT, "name", TEXT)'''
	result = cursor.execute(createTableSQL)
else:
	print '''NOTE | pins table exists.'''

try:
	returnData = urllib.urlopen(url).read()
except Exception, e:
	print 'Error: Unable to connect to pinboard API'
	exit()
else:
	returnJSON = json.loads(returnData)
finally:
	pass

hashes = []
for info in returnJSON:
	h = info['hash'].encode('utf-8')
	hashes.append(h)

	dateStr = info['time']
	href = info['href'].encode('utf-8')
	dt = dateutil.parser.parse(dateStr)
	epoch = int(dt.strftime('%s'))
	tags = sanitizeTags(info['tags'])
	name = sanitizeName(info['extended'])
	tagList = tags.split()

	#	does this tag already exist in the database?
	checkHashStmt = '''SELECT COUNT(*) FROM pins WHERE hash = "%s"''' % h
	cursor.execute(checkHashStmt)
	result = cursor.fetchone()
	if result[0] == 0:
		print '''%s | %s | %d | %s''' % (h,href,int(epoch),tags)
		insertStm = '''INSERT INTO pins (hash, href, date, tags, name) VALUES ("%s", "%s", %d, "%s", '%s')''' % (h,href,epoch,tags,name)
		conn.execute(insertStm)
		conn.commit()

		#	since this is a new entry, create a webloc file for it
		#	plistlib.dump(value, fp, *, fmt=FMT_XML, sort_keys=True, skipkeys=False)
		fn = '''%s/%s.webloc''' % (args['webloc'].strip(),name)
		print fn
		#fileobj = open(fn,'wb')
		plistDict = {}
		plistDict["URL"] = href
		plistlib.writePlist(plistDict,fn)

		#	tag the files
		tagList = ','.join(map(str, tagList))
		tagcmd = '''/usr/local/bin/tag --add %s %s''' % (tagList, fn)
		subprocess.call(shlex.split(tagcmd))
	else:
		#	check for any changes
		chgStmt = '''SELECT * FROM pins WHERE hash = "%s"''' % h
		print chgStmt
		cursor.execute(chgStmt)
		result = cursor.fetchone()
		if result[2] != epoch:
			print '''UPDATE | item with hash %s''' % h
			alterStmt = '''UPDATE pins SET href = "%s", date = "%d", tags = "%s", name = "%s"''' % (href, epoch, tags,name)
			conn.execute(alterStmt)
			conn.commit()

#	deal with deletions

findHashStmt = '''SELECT hash,name FROM pins'''
cursor.execute(findHashStmt)
localItems = cursor.fetchall()
localHashList = [r["hash"] for r in localItems]
for h in set(localHashList).difference(hashes):
	#	this is an item to remove
	deleteStmt = '''DELETE FROM pins WHERE hash = "%s"''' % hsh
	conn.execute(deleteStmt)
	conn.commit()
	#	remove local file
	name = (item for item in localItems if item["hash"] == h).next()["name"]
	fn = '''%s/%s.webloc''' % (args['webloc'].strip(),name)
	os.remove(fn)
	print '''NOTE | Deleted item %s''' % h
conn.close()



