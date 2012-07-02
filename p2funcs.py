import math

#######################################################
def Along(lam, a, b):
	assert(lam >= 0.0 and lam <= 1.0)
	return (b[0] * lam + a[0] * (1.0 - lam), b[1] * lam + a[1] * (1.0 - lam))

def InvAlong(val, a, b):
	if val == a:
		return 0.0
	elif val == b:
		return 1.0

	return (val - a)/(b - a)

#######################################################
def Arg(p):
	res = math.atan2(p[1], p[0])
	if (res < 0.0):
		res += 2 * math.pi
	return res

#######################################################
def APerp(vec):
	return (-vec[1], vec[0])

#######################################################
def CPerp(vec):
	return (vec[1], -vec[0])

#######################################################
def NAPerp(vec):
	return Norm((-vec[1], vec[0]))

#######################################################
def NCPerp(vec):
	return Norm((vec[1], -vec[0]))

#######################################################
def Len(vec):
	return math.sqrt(sqLen(vec))

#######################################################
def sqLen(vec):
	return (vec[0] * vec[0] + vec[1] * vec[1])

#######################################################
def Dot(a, b):
	r = a[0] * b[0]
	for i in range(1, len(a)):
		r += a[i] * b[i]

	return r

	
#######################################################
def Rot(vec, theta):
	c = math.cos(theta)
	s = math.sin(theta)
	return (vec[0] * c + vec[1] * s, vec[1] * c - vec[0] * s)

#######################################################
def sqDist(a, b):
	assert len(a) == len(b)
	v = tuple([a[i] - b[i] for i in range(len(a))])
	return Dot(v, v)

#######################################################
def Dist(a, b):
	return math.sqrt(sqDist(a, b))


#######################################################
def Norm(a):
	l = math.sqrt(Dot(a, a))
	return (a[0] / l, a[1] / l)

#######################################################
def Acos(a):
	if a > 1.0:
		a = 1.0
	elif a < -1.0:
		a = -1.0

	return math.acos(a)

#######################################################
def Intersect(pt0, dir0, pt1, dir1):

	if (dir0[0] == 0.0 and dir0[1] == 0.0) or (dir1[0] == 0.0 and dir1[1] == 0.0):
		return None

	assert math.fabs(Dist(dir0, (0., 0.)) - 1.0) < 0.001
	assert math.fabs(Dist(dir1, (0., 0.)) - 1.0) < 0.001

	dp = Dot(dir0, dir1)
	if dp == -1.0 or dp == 1.0:
		return None

	p10 = (pt1[0] - pt0[0], pt1[1] - pt0[1])

	if dir1[0] == 0 and dir0[0] == 0:
		return None

	if abs(dir1[0]) > abs(dir0[0]):

		ratio = dir1[1] / dir1[0]
		llam = (ratio * p10[0] - p10[1]) / (ratio * dir0[0] - dir0[1])
		lmue = (p10[0] - llam * dir0[0]) / dir1[0]

	else:
		ratio = dir0[1] / dir0[0]
		nom = (dir1[1] - ratio * dir1[0])
		if nom == 0.0:
			return None# give up
		lmue = (p10[1] - ratio * p10[0]) / (dir1[1] - ratio * dir1[0])
		llam = (p10[0] - dir1[0] * lmue) / dir0[0]

	k = (pt0[0] + llam * dir0[0], pt0[1] + llam * dir0[1])
	l = (pt1[0] - lmue * dir1[0], pt1[1] - lmue * dir1[1])

	eps = 0.2
	if Dist(k, l) >= eps:
		pass
		#print "pt0 = ", pt0
		#print "dir0 = ", dir0
		#print "pt1 = ", pt1
		#print "dir1 = ", dir1
		#print "k, l, dist", k, l, Dist(k, l)
		#assert False

	return ((k[0] + l[0]) / 2.0, (k[1] + l[1]) / 2.0)


#######################################################
def IsClockwise(plist):
	assert plist[0] == plist[-1]
	assert len(plist) > 3
	# find leftmost vertex
	xvals = [(plist[i][0], plist[i][1], i) for i in range(len(plist) - 1)]
	xvals.sort()
	ileft = xvals[0][2]

	iprev = ileft - 1
	if iprev == -1:
		iprev = len(plist) - 2
	inext = ileft + 1
	if inext == len(plist) - 1:
		inext = 0

	assert plist[iprev][0] >= plist[ileft][0] and plist[inext][0] >= plist[ileft][0]
	assert plist[iprev][0] != plist[ileft][0] or plist[inext][0] != plist[ileft][0] # if this breaks we have to find a corner

	# cross product
	pprev = plist[iprev]
	pp = plist[ileft]
	pnext = plist[inext]

	x0, y0 = pprev[0] - pp[0], pprev[1] - pp[1]
	x1, y1 = pnext[0] - pp[0], pnext[1] - pp[1]
	direction = x0 * y1 - x1 * y0
	if direction == 0:
		print "WARNING: Does this polygon have no area? ", plist
	return (direction > 0)


#######################################################
def PointInPolygon(plist, p, debug=False):
	if debug:
		print p
		print plist
	# point is inside if number of intersections of half-scanline is not null and an odd number
	nintersections = 0
	for ix in range(1,len(plist)):
		a, b = plist[ix - 1], plist[ix]
		if (a[1] > p[1]) != (b[1] > p[1]): # both points above test point
			lam = 1.0 - (b[1] - p[1]) / (b[1] - a[1])
			xc = a[0] + (b[0] - a[0]) * lam # the x component of an intersection point of half-scan line an polygon segment
			if xc > p[0]:
				nintersections += 1
	return ((nintersections % 2) == 1)

# along proportion and distance of point p to line l0, l1
def LamAlongDistsq(p, l0, l1):
	l0p = (p[0] - l0[0], p[1] - l0[1])
	l01 = (l1[0] - l0[0], l1[1] - l0[1])
	sqdl01 = sqDist(l0, l1)

	if sqdl01 > 0:
		lam = Dot(l0p, l01) / sqdl01
	else:
		lam = -1.0

	if (lam < 0):
		return 0.0, sqDist(p, l0)
	elif (lam > 1.0):
		return 1.0, sqDist(p, l1)
	else:
		pperp = Along(lam, l0, l1)
		dist = sqDist(pperp, p)
		return lam, dist


def GetArea(poly): # anticlockwise is positive area
    darea = 0
    for i in range(1, len(poly)):
        x0, y0 = poly[i - 1]
        x1, y1 = poly[i]
        darea += (x0 * y1 - x1 * y0)
    return darea / 2.0

def QuickOffset(poly, offset):
    # a quick offset by moving each node of closed polygon perpendicular
    assert poly[0] == poly[-1]
    if not IsClockwise(poly):
        offset = -offset
    polynew = [ ]
    for i in range(len(poly)):
        iprev = i - 1
        if iprev == -1:
            iprev = len(poly) - 2
        inext = i + 1
        if inext == len(poly):
            inext = 1
        pp = poly[iprev]
        p = poly[i]
        pn = poly[inext]

        v0 = (pp[0] - p[0], pp[1] - p[1])
        v0perp = APerp(v0)
        v1 = (pn[0] - p[0], pn[1] - p[1])
        v1perp = CPerp(v1)
        voffset = Norm((v0perp[0] + v1perp[0], v0perp[1] + v1perp[1]))
        poffset = (p[0] + offset * voffset[0], p[1] + offset * voffset[1])
        polynew.append(poffset)
    assert len(polynew) == len(poly)
    return polynew


def InvDarg(a):
	# we permit up to the range of 8
	if a >= 4.0: 
		a -= 4.0 
	assert (0.0 <= a) and (a < 4.0)
	if a < 2.0:
		lu = 1.0 - a
	else:
		lu = a - 3.0

		
	if a < 3.0:
		if a > 1.0:
			lv = 2.0 - a
		else:
			lv = a
	else:
		lv = a - 4.0
	return (lu, lv)
