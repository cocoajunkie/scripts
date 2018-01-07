#!/usr/bin/env python3

# Creates a pdf file with labels for a series of resistor values.
# Written for any type of label sheet but tested below with Avery 5422 labels.
# Quick start: 
# 1. Specify the series of values and label sheet dimensions (ALL UNITS ARE IN INCHES) here:

# For example, this will print 61 labels for E12 series from 10 ohms to 1 mega-ohm
series = [10, 12, 15, 18, 22, 27, 33, 39, 47, 56, 68, 82]
max_value = 1 * 10 ** 6

import collections
Dim = collections.namedtuple('Dim', ['w', 'h'])
# page width and height 
PAGE_DIMENSIONS = Dim(4, 6) 
# label width and height 
LABEL_DIMENSIONS = Dim(1.75, 0.5) 
# horizontal (left/right) and vertical (top/bottom) page margins
MARGINS = (3/16, 0.5)
# horizontal and vertical pitch (distance from left/top label edge to its horiz/vert neighbor)
PITCH = (LABEL_DIMENSIONS.w + 1/8, LABEL_DIMENSIONS.h)

# 2. Run script passing a pdf filename to create

# 3. Print labels!


import sys
import reportlab
import reportlab.pdfgen.canvas
from reportlab.lib.units import inch

Rect = collections.namedtuple('Rect', ['x', 'y', 'w', 'h'])

if len(sys.argv) < 2:
	print("usage: " + sys.argv[0] + " <pdf_file>")
	exit()
canvas = reportlab.pdfgen.canvas.Canvas(sys.argv[1], pagesize=(PAGE_DIMENSIONS.w * inch, PAGE_DIMENSIONS.h * inch))

colors = [reportlab.lib.colors.black,
	reportlab.lib.colors.brown,
	reportlab.lib.colors.red,
	reportlab.lib.colors.orange,
	reportlab.lib.colors.yellow,
	reportlab.lib.colors.green,
	reportlab.lib.colors.blue,
	reportlab.lib.colors.violet,
	reportlab.lib.colors.grey,
	reportlab.lib.colors.white]

stripes1and2 = [(colors[int(str(x)[0])], colors[int(str(x)[1])]) for x in series]

class LabelRenderer:
	def __init__(self):
		self.pos = 0 # position in resistor series list to draw next
		self.decade = 0

	def draw_label(self, rect):
		canvas.setStrokeColor(reportlab.lib.colors.grey)
		canvas.setFillColor(reportlab.lib.colors.black)
		canvas.setLineWidth(1)
		canvas.rect(rect.x * inch, rect.y * inch, rect.w * inch, rect.h * inch)

		v = series[self.pos] *  10 ** self.decade
		
		v_with_units = (v, '\u2126')

		if (v >= 1000 and v < 10 ** 6):
			v_with_units = (v/1000, "K" + v_with_units[1])
		elif (v >= 10 ** 6):
			v_with_units = (v/10 ** 6, "M" + v_with_units[1])

		v_str = ("{:.5g} " + v_with_units[1]).format(v_with_units[0])
		print(v_str)

		canvas.setStrokeColor(reportlab.lib.colors.black)
		canvas.setFont("Helvetica-Bold", 18)
		y = (rect.y + 1/8)
		canvas.drawString((rect.x + 1/8) * inch, y * inch, v_str)
		
		stripes = list(stripes1and2[self.pos]) + [colors[self.decade]]
		stripes.reverse()
		stripeD = Dim(w = 1/8, h = 1/4)
		x = rect.x + rect.w - 1/8 - stripeD.w
		for s in stripes:
			canvas.setFillColor(s)
			canvas.setStrokeColor(reportlab.lib.colors.grey)
			canvas.rect(x * inch, y * inch, stripeD.w * inch, stripeD.h * inch, stroke = 1, fill = 1)
			x -= 1/16 + stripeD.w

		self.pos += 1
		if self.pos == len(series):
			self.decade += 1
			self.pos = 0

		return (v != max_value)

	def page_break(self):
		canvas.showPage()

class LabelPrinter:
	def __init__(self, page_dim, label_dim, margins, pitch):
		self.pageW, self.pageH = page_dim.w, page_dim.h
		self.labelW, self.labelH = label_dim.w, label_dim.h
		self.marginH, self.marginV = margins[0], margins[1]
		self.pitchH, self.pitchV = pitch[0], pitch[1]

	def print_all(self, renderer):
		x = self.marginH
		y = self.marginV
		while (renderer.draw_label(Rect(x, y, self.labelW, self.labelH))):
			if (x + self.labelW + self.marginH) == self.pageW:
				if (y + self.labelH + self.marginV) == self.pageH:
					renderer.page_break()
					x = self.marginH
					y = self.marginV
				else:
					x = self.marginH
					y += self.pitchV
			else:
				x += self.pitchH


		renderer.page_break()

printer = LabelPrinter(PAGE_DIMENSIONS, LABEL_DIMENSIONS, MARGINS, PITCH)
printer.print_all(LabelRenderer())
canvas.save()
