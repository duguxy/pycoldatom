import os

def getAutosaveFileName(time, filesuffix='', fileinfix='', foldersuffix=''):
	subfolder = time[0]
	fileprefix = '%sT%s' % (time[0], time[1])
	destfolder = "%s_%s" % (subfolder, foldersuffix)
	destfile = os.path.join(destfolder, "%s-%s-%s" % (fileprefix, fileinfix, filesuffix))
	return destfile

if __name__ == '__main__':
	date, time = ['2015-01-06', '17-16-01']
	print(getAutosaveFileName((date, time), 'suffix', 'infix', 'foldersuffix'))
