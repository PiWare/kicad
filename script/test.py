#!/usr/bin/python

import fp
import config
cfg = config.Config("config")

#from footprint import *
#import footprint.wired

registered_footprints = {}

class metaclass_register(type):
	def __init__(self, name, bases, nmspc):
		super(metaclass_register, self).__init__(name, bases, nmspc)
		registered_footprints[name] = self

class class1(object):
	__metaclass__ = metaclass_register
 
	def __init__(self, name):
		print "Construct class1"
		self.text = "class1"
		self.name = name
		pass

	def foo(self):
		print self.text
		print self.name
 
class class2(class1):
 
	def __init__(self, name, desc):
		super(class2, self).__init__(name)
		self.text += "!"
		self.desc = desc
		pass

	def foo(self):
		d = fp.line("12", 0, 0, 10, 10, 0.1)
		print d.render()
		print self.text
		print self.name
		print self.desc
 
print registered_footprints
 
t = registered_footprints['class1']("Name")
t.foo()
 
t = registered_footprints['class2']("Name", "Beschreibung")
t.foo()

#t = registered_footprints['footprint']("name")
#print t.render()
