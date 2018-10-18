import math

def JuniorBirthdayProblem():
	days = 365*2.0
	p = 1.0
	for n in xrange(2, 200):
		p *= (1.0 - (n-1)/days)
		print n, 1.0 - p
	
if __name__ == '__main__':
	JuniorBirthdayProblem()