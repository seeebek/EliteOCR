#!/usr/bin/env python
"""QImage <-> numpy.ndarray conversion module.

*** ATTENTION: This code is outdated - I released a better extension
*** named 'qimage2ndarray' (that completes all TODO items below) in
*** the meantime, which is available via PyPI and here:
*** http://kogs-www.informatik.uni-hamburg.de/~meine/software/qimage2ndarray/

This supports conversion in both directions; note that in contrast to
C++, in Python it is not possible to convert QImages into ndarrays
without copying the data.  The conversion functions in the opposite
direction however do not copy the data.

TODO:
- support record arrays in rgb2qimage
  (i.e. grok the output of qimage2numpy)
- support unusual widths/alignments also in gray2qimage and
  rgb2qimage
- make it possible to choose between views and copys of the data
  (eventually in both directions, when implemented in C++)
- allow for normalization in numpy->QImage conversion
  (i.e. to quickly visualize images with different value ranges)
- implement in C++
"""

import numpy
from PyQt4.QtGui import QImage, QColor

bgra_dtype = numpy.dtype({'b': (numpy.uint8, 0),
						  'g': (numpy.uint8, 1),
						  'r': (numpy.uint8, 2),
						  'a': (numpy.uint8, 3)})

def qimage2numpy(qimage, dtype = 'array'):
	"""Convert QImage to numpy.ndarray.  The dtype defaults to uint8
	for QImage.Format_Indexed8 or `bgra_dtype` (i.e. a record array)
	for 32bit color images.  You can pass a different dtype to use, or
	'array' to get a 3D uint8 array for color images."""
	result_shape = (qimage.height(), qimage.width())
	temp_shape = (qimage.height(),
				  qimage.bytesPerLine() * 8 / qimage.depth())
	if qimage.format() in (QImage.Format_ARGB32_Premultiplied,
						   QImage.Format_ARGB32,
						   QImage.Format_RGB32):
		if dtype == 'rec':
			dtype = bgra_dtype
		elif dtype == 'array':
			dtype = numpy.uint8
			result_shape += (4, )
			temp_shape += (4, )
	elif qimage.format() == QImage.Format_Indexed8:
		dtype = numpy.uint8
	else:
		raise ValueError("qimage2numpy only supports 32bit and 8bit images")
	# FIXME: raise error if alignment does not match
	buf = qimage.bits().asstring(qimage.numBytes())
	result = numpy.frombuffer(buf, dtype).reshape(temp_shape)
	if result_shape != temp_shape:
		result = result[:,:result_shape[1]]
	if qimage.format() == QImage.Format_RGB32 and dtype == numpy.uint8:
		result = result[...,:3]
	return result

def numpy2qimage(array):
	if numpy.ndim(array) == 2:
		return gray2qimage(array)
	elif numpy.ndim(array) == 3:
		return rgb2qimage(array)
	raise ValueError("can only convert 2D or 3D arrays")

def gray2qimage(gray):
	"""Convert the 2D numpy array `gray` into a 8-bit QImage with a gray
	colormap.  The first dimension represents the vertical image axis.

	ATTENTION: This QImage carries an attribute `ndimage` with a
	reference to the underlying numpy array that holds the data. On
	Windows, the conversion into a QPixmap does not copy the data, so
	that you have to take care that the QImage does not get garbage
	collected (otherwise PyQt will throw away the wrapper, effectively
	freeing the underlying memory - boom!)."""
	if len(gray.shape) != 2:
		raise ValueError("gray2QImage can only convert 2D arrays")

	gray = numpy.require(gray, numpy.uint8, 'C')

	h, w = gray.shape

	result = QImage(gray.data, w, h, QImage.Format_Indexed8)
	result.ndarray = gray
	for i in range(256):
		result.setColor(i, QColor(i, i, i).rgb())
	return result

def rgb2qimage(rgb):
	"""Convert the 3D numpy array `rgb` into a 32-bit QImage.  `rgb` must
	have three dimensions with the vertical, horizontal and RGB image axes.

	ATTENTION: This QImage carries an attribute `ndimage` with a
	reference to the underlying numpy array that holds the data. On
	Windows, the conversion into a QPixmap does not copy the data, so
	that you have to take care that the QImage does not get garbage
	collected (otherwise PyQt will throw away the wrapper, effectively
	freeing the underlying memory - boom!)."""
	if len(rgb.shape) != 3:
		raise ValueError("rgb2QImage can only convert 3D arrays")
	if rgb.shape[2] not in (3, 4):
		raise ValueError("rgb2QImage can expects the last dimension to contain exactly three (R,G,B) or four (R,G,B,A) channels")

	h, w, channels = rgb.shape

	# Qt expects 32bit BGRA data for color images:
	bgra = numpy.empty((h, w, 4), numpy.uint8, 'C')
	bgra[...,0] = rgb[...,2]
	bgra[...,1] = rgb[...,1]
	bgra[...,2] = rgb[...,0]
	if rgb.shape[2] == 3:
		bgra[...,3].fill(255)
		fmt = QImage.Format_RGB32
	else:
		bgra[...,3] = rgb[...,3]
		fmt = QImage.Format_ARGB32

	result = QImage(bgra.data, w, h, fmt)
	result.ndarray = bgra
	return result

if __name__ == '__main__':
    import pylab
    i = QImage()
#    i.load("qimage2ndarray_test.png")
    i.load("qimage2ndarray_test_lenna.jpg")
    v = qimage2numpy(i, "rec")
    v2 = qimage2numpy(i, "array")
    pylab.imshow(v2[...,0])
    pylab.show()

	# v is a recarray; make it MPL-compatible for showing:
    rgb = numpy.empty(v.shape + (3, ), dtype = numpy.uint8)
    rgb[...,0] = v["r"]
    rgb[...,1] = v["g"]
    rgb[...,2] = v["b"]
    pylab.imshow(rgb)
    pylab.show()
