# -*- coding: utf-8 -*-
from urllib2 import urlopen
from lxml.html import soupparser
from lxml import etree
from os import path, system
from xml.dom import minidom

__author__ = "C.Wilhelm"
__license__ = "AGPL v3"

uri = "http://www.gesetze-im-internet.de/"
nopdf = "substring(@href, string-length(@href)-3)!='.pdf'" # lxml supports XPath 1.0
html = urlopen(uri+"aktuell.html").read()
element = soupparser.fromstring(html)
for link in element.xpath("//a[number(text())]"):
	html = urlopen(uri+link.attrib["href"]).read()
	element = soupparser.fromstring(html)
	for link in element.xpath("//*[@id = 'container']//a[%s]" % nopdf):
		response = urlopen(uri+link.attrib["href"])
		element = soupparser.fromstring(response.read())
		current_url = path.dirname(response.geturl())
		short_name = path.split(current_url)[-1]#.strip("-_123456789")
		for link in element.xpath("//h2//a[%s]" % nopdf):
			html = urlopen(current_url+"/"+link.attrib["href"]).read()
			element = soupparser.fromstring(html)
			output = etree.tostring(element, encoding="utf-8", method="xml")
			output = minidom.parseString(output).toprettyxml()
			f = open('tmp/'+short_name, 'w')
			f.write(output.encode("utf-8"))
			f.close()
