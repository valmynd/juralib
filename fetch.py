# -*- coding: utf-8 -*-
from urllib2 import urlopen
from lxml import etree, html
from os import path, system
from xml.dom import minidom

from zipfile import ZipFile, BadZipfile
from StringIO import StringIO

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

def write_xml(url, filename):
	remotefile = urlopen(url)
	memoryfile = StringIO(remotefile.read())
	# using remotefile directly would cause AttributeError: addinfourl instance has no attribute 'seek'
	zipfile = ZipFile(memoryfile)
	zipfile.extractall(path="tmp/%s/" % filename)
	zipfile.close()

def write_markdown(url, filename):
	system("pandoc --atx-headers -s -r html %s -o %s.md" % (url, filename))

def fetch():
	uri = "http://www.gesetze-im-internet.de/"
	content = urlopen(uri+"aktuell.html").read()
	element = html.fromstring(content)
	for link in element.xpath("//a[@class = 'alphabet']"):
		content = urlopen(uri+link.attrib["href"]).read()
		element = html.fromstring(content)
		xpath_nopdf = "substring(@href, string-length(@href)-3)!='.pdf'" # lxml supports XPath 1.0
		for link in element.xpath("//*[@id = 'container']//a[%s]" % xpath_nopdf):
			response = urlopen(uri+link.attrib["href"])
			element = html.fromstring(response.read())
			current_url = path.dirname(response.geturl())
			short_name = path.split(current_url)[-1]#.strip("-_123456789")
			xpath_xmlonly = "substring(@href, string-length(@href)-3)='.zip'"
			for link in element.xpath("//h2//a[%s]" % xpath_xmlonly):
				write_xml(current_url+"/"+link.attrib["href"], filename=short_name)

write_xml("http://www.gesetze-im-internet.de/alg/xml.zip", "alg") # contains tables
write_xml("http://www.gesetze-im-internet.de/bgb/xml.zip", "bgb")
write_xml("http://www.gesetze-im-internet.de/hgb/xml.zip", "hgb")
write_xml("http://www.gesetze-im-internet.de/gmbhg/xml.zip", "gmbhg")
write_xml("http://www.gesetze-im-internet.de/aktg/xml.zip", "aktg")
#fetch()
