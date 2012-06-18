# -*- coding: utf-8 -*-
from urllib2 import urlopen
from lxml import etree, html
from os import path, system
from xml.dom import minidom

__author__ = "C.Wilhelm"
__license__ = "AGPL v3"

def write_html(url, filename):
	root_element = etree.Element("Gesetz")
	content = urlopen(url).read()
	element = html.fromstring(content)
	element = element.xpath("//*[@id = 'paddingLR12']")[0]
	for unwanted in element.xpath("//*[name() = 'a' or name() = 'script']"):
		unwanted.getparent().remove(unwanted)
	### prepare HTML tables (pandoc cannot handle them)
	#handle_html_tables(element)
	output = etree.tostring(element, encoding="utf-8", method="xml")
	#output = minidom.parseString(output).toprettyxml()
	#output = element.xpath("string()")
	f = open('tmp/'+filename, 'w')
	f.write(output)#.encode("utf-8"))
	f.close()
	write_markdown(	url='tmp/'+filename,
					filename='tmp/'+filename)

def write_markdown(url, filename):
	system("pandoc -s -r html %s -o %s.md" % (url, filename))

def fetch():
	uri = "http://www.gesetze-im-internet.de/"
	nopdf = "substring(@href, string-length(@href)-3)!='.pdf'" # lxml supports XPath 1.0
	content = urlopen(uri+"aktuell.html").read()
	element = html.fromstring(content)
	for link in element.xpath("//a[@class = 'alphabet']"):
		content = urlopen(uri+link.attrib["href"]).read()
		element = html.fromstring(content)
		for link in element.xpath("//*[@id = 'container']//a[%s]" % nopdf):
			response = urlopen(uri+link.attrib["href"])
			element = html.fromstring(response.read())
			current_url = path.dirname(response.geturl())
			short_name = path.split(current_url)[-1]#.strip("-_123456789")
			for link in element.xpath("//h2//a[%s]" % nopdf):
				write_html(current_url+"/"+link.attrib["href"], short_name)

write_html("http://www.gesetze-im-internet.de/alg/BJNR189100994.html", "alg") # contains tables
write_html("http://www.gesetze-im-internet.de/bgb/BJNR001950896.html", "bgb")
write_html("http://www.gesetze-im-internet.de/bgb/BJNR001950896.html", "hgb")
#fetch()
