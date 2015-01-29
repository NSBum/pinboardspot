import json
import urllib
import sqlite3
import dateutil.parser
import plistlib
import subprocess
import sys


url = 'https://%s:%s@api.pinboard.in/v1/posts/all?format=json' % (uname, pword)
dbpath = '/Users/alanduncan/torrential/web/pinboardsync.db'
weblocPath = '/Users/alanduncan/torrential/web'

try:
	conn = sqlite3.connect(dbpath)
except Exception, e:
	print 'Error: Unable to connect to pinboardsync db.'
	exit()
else:
	print "Connected to db"
finally:
	pass

#	do we have the right table?
tableSQL = "SELECT tbl_name FROM sqlite_master WHERE type='table'"
cursor = conn.cursor()
found = False
cursor.execute(tableSQL)
for row in cursor.fetchall():
	if row[0] == 'pins':
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

for info in returnJSON:
	h = info['hash'].encode('utf-8')
	dateStr = info['time']
	href = info['href'].encode('utf-8')
	dt = dateutil.parser.parse(dateStr)
	epoch = int(dt.strftime('%s'))
	tags = info['tags'].encode('utf-8')
	name = info['extended'].encode('utf-8').replace('\"','')
	name = name.replace('\'','')
	name = name.replace('/','')
	# info = (data[:75] + '..') if len(data) > 75 else data
	name = (name[:30]) if len(name) > 30 else name
	tagList = tags.split()

	#	does this tag already exist in the database?
	checkHashStmt = '''SELECT COUNT(*) FROM pins WHERE hash = "%s"''' % h
	cursor.execute(checkHashStmt)
	result = cursor.fetchone()
	if result[0] == 0:
		# print '''%s | %s | %d | %s''' % (h,href,int(epoch),tags)
		insertStm = '''INSERT INTO pins (hash, href, date, tags, name) VALUES ("%s", "%s", %d, "%s", '%s')''' % (h,href,epoch,tags,name)
		conn.execute(insertStm)
		conn.commit()

		#	since this is a new entry, create a webloc file for it
		#	plistlib.dump(value, fp, *, fmt=FMT_XML, sort_keys=True, skipkeys=False)
		fn = '''%s/%s.webloc''' % (weblocPath,name)
		#fileobj = open(fn,'wb')
		plistDict = {}
		plistDict["URL"] = href
		plistlib.writePlist(plistDict,fn)

		#	tag the files
		tagList = ','.join(map(str, tagList))
		subprocess.call(["tag","--add",tagList,fn])
	else:
		#	check for any changes
		chgStmt = '''SELECT * FROM pins WHERE hash = "%s"''' % h
		cursor.execute(chgStmt)
		result = cursor.fetchone()
		if result[2] != epoch:
			alterStmt = '''UPDATE pins SET href = "%s", date = "%d", tags = "%s", name = "%s"''' % (href, epoch, tags,name)
			conn.execute(alterStmt)
			conn.commit()
conn.close()



