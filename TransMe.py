# -*- coding: UTF-8 -*

import os,re
cwd = os.getcwd()

src = os.path.join(cwd, 'test')
# src = '/Users/InRuan/Desktop/templates'

dst = os.path.join(src, 'locals')

langs = ['zh_CN', 'en']

trans = {

}
lencmp = lambda v1,v2:len(v1)-len(v2) if len(v1)!=len(v2) else cmp(v1, v2)
trans = [(k,v) for k,v in trans.items()]
trans = sorted(trans, cmp=lambda v1,v2:lencmp(v1[0], v2[0]), reverse=True)
# print trans
noasciip = re.compile(u'([\u2E80-\u9FFF]+)')

untrans = {}


def checkfilepath(filepath):
	global dst
	return not filepath.startswith(dst)

def checktrans(text):
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
						res = checktrans(dsttext)
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

for k,v in sorted(untrans.items(), lambda v1,v2:lencmp(v1[0],v2[0]), reverse=True):
	print k+u':'+(','.join(v['files']))+" "+(','.join(v['langs']))
	pass
