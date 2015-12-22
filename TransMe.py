# -*- coding: UTF-8 -*

import sys,os,re,time
import xlrd, xlwt


starttime = time.time()
def err(s):
	sys.stderr.write(s)
	sys.stderr.write('\r\n')

cwd = os.getcwd()
langs = []
srctrans = []
mainlang = 'zh_CN'
transxls = os.path.join(cwd, 'trans.xls')

try:
	bk = xlrd.open_workbook(transxls)
	sh = bk.sheets()[0]
	icol = range(0,sh.ncols)
	if sh.nrows==0:
		err("xls empty")
		exit()
	langs = [l for l in sh.row_values(0)]
	if None in langs or '' in langs:
		err('language can\'t be empty')
		exit()
	if mainlang not in langs:
		err('main language not in xls')
		exit()
	for i in range(1,sh.nrows):
		row_data = sh.row_values(i)
		srctrans.append(dict([(langs[n], row_data[n])  for n in icol if row_data[n]]))
except:
	err('load trans from xls %s failed'%transxls)
	exit()

lencmp = lambda v1,v2:len(v1)-len(v2) if len(v1)!=len(v2) else cmp(v1, v2)

trans = []
mainlangkeys = []
for i,t in enumerate(srctrans):
	if not t[mainlang]:
		err(u'not provide %s at line %d of %s'%(mainlang, i+1, transxls))
	elif t[mainlang] not in mainlangkeys:
		mainlangkeys.append(t[mainlang])
		trans.append((t[mainlang], t),)

trans = sorted(trans, cmp=lambda v1,v2:lencmp(v1[0], v2[0]), reverse=True)



src = os.path.join(cwd, 'test')
# src = '/Users/InRuan/Desktop/templates'

dst = os.path.join(src, 'locals')


# print trans
noasciip = re.compile(u'([\u2E80-\u9FFF]+)')

untrans = {}


def checkfilepath(filepath):
	global dst
	return not filepath.startswith(dst) and (filepath.lower().endswith('.html') or filepath.lower().endswith('.txt'))

def checktrans(text, lan):
	global noasciip
	return noasciip.findall(text)

for parent,dirnames,filenames in os.walk(src):
	for filename in filenames:
		filepath = os.path.join(parent, filename)
		if not checkfilepath(filepath): continue
		srcfile = filepath
		filepath = srcfile.replace(src, '')
		try:
			with open(srcfile, "r+") as srcf:
				srctext = srcf.read().decode('utf8')
				for l in langs:
					if l == mainlang:
						continue
					dstfile = srcfile.replace(src, os.path.join(dst, l))
					dstp = os.path.dirname(dstfile)
					if not os.path.isdir(dstp):
						os.makedirs(dstp)
					with open(dstfile, "w+") as dstf:
						dsttext = srctext
						for k,v in trans:
							if l in v:
								dsttext = dsttext.replace(k, v[l])

						dstf.write(dsttext.encode('utf8'))
						res = checktrans(dsttext, l)
						if res:
							for r in res:
								if r not in untrans:
									untrans[r] = {'files':[filepath], 'langs':[l]}
									continue
								if l not in untrans[r]['langs']:
									untrans[r]['langs'].append(l)
								if filepath not in untrans[r]['files']:
									untrans[r]['files'].append(filepath)
		except:
			print 'failed when: %s'%filepath

wb = xlwt.Workbook(encoding='utf-8')
sh = wb.add_sheet(u'Sheet1')
langsmap = dict([(l,i) for i,l in enumerate(langs)])
for i,l in enumerate(langs):
	sh.write(0, i, l)

emptystyle = xlwt.easyxf('pattern: pattern solid, fore_colour rose; font: bold on;');
addstyle = xlwt.easyxf('pattern: pattern solid, fore_colour red; font: bold on;');
rows = 1
for m,t in trans:
	for l in langs:
		if l in t and t[l]:
			sh.write(rows, langsmap[l], t[l])
		else:
			sh.write(rows, langsmap[l], '',emptystyle)
	rows += 1



if untrans:
	print 'to do:'
	for k,v in sorted(untrans.items(), lambda v1,v2:lencmp(v1[0],v2[0]), reverse=True):
		if k not in mainlangkeys:
			mainlangkeys.append(k)
			sh.write(rows, langsmap[mainlang], k, addstyle)
			rows += 1
		print '\t'+ k.encode('utf8')

bakfile = transxls+".bak"
with open(transxls, 'rb') as src:
	with open(bakfile, 'wb') as dst:
		dst.write(src.read())

wb.save(transxls)
dtransxls = transxls
os.remove(bakfile)
print '%s --> %s'%(mainlang, ','.join([l for l in langs if l != mainlang]))
print '%ss'%(time.time()-starttime)


