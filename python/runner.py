import tailer

for line in tailer.follow(open('block.txt','r')):
	if 'progress=continue' in line:
		print 'we continue'

	elif 'progress=end' in line:
		print 'we stop'
		break

	else:
		print 'unknown line: %s' % line
