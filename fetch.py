# -*- coding: utf-8 -*-
from urllib2 import urlopen
from lxml import etree, html
from xml.dom import minidom

from zipfile import ZipFile, BadZipfile
from StringIO import StringIO
from os import listdir, path

__author__ = "C.Wilhelm"
__license__ = "AGPL v3"

def write_xml(url, filename):
	remotefile = urlopen(url)
	memoryfile = StringIO(remotefile.read())
	# using remotefile directly would cause AttributeError: addinfourl instance has no attribute 'seek'
	zipfile = ZipFile(memoryfile)
	zipfile.extractall(path="tmp/%s/" % filename)
	zipfile.close()

def write_markdown(filename_in, filename_out):
	system("pandoc --atx-headers -s -r html %s -o %s.md" % (filename_in, filename_out))

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

def index():
	"extract metadata for all fetched xml files in ./tmp/"
	# structure: title | filename | [keyword1,keyword2,title]
	# example: ./tmp/alg/BJNR189100994.xml | [ALG]
	dtd = etree.DTD("gii-norm.dtd")
	laws = etree.Element("laws")
	for name in listdir("./tmp/"):
		subpath = path.join("./tmp/", name)
		if not path.isdir(subpath):
			continue
		pname = name # the index.xml should contain relative pathes
		for name in listdir(subpath):
			if name.endswith(".xml"):
				keywords = set()
				titles = set()
				filename = path.join(subpath, name)
				dokumente = etree.parse(filename)
				assert(dtd.validate(dokumente))
				# <!ELEMENT dokumente (norm*)> # Regelfall: erste "Norm" enthält Metadaten für Gesamtdokument, zweite "Norm" enthält Inhaltsverzeichnis
				firstnorm = dokumente.find("norm")
				# <!ELEMENT metadaten (jurabk+, amtabk?, ausfertigung-datum?, fundstelle*, kurzue?, langue?, gliederungseinheit?, enbez?, titel?, standangabe*)>
				keywords.update(k.lower() for k in firstnorm.xpath("metadaten/jurabk/text()"))
				keywords.update(k.lower() for k in firstnorm.xpath("metadaten/amtabk/text()"))
				titles.update(firstnorm.xpath("metadaten/langue/text()"))
				titles.update(firstnorm.xpath("metadaten/titel/text()"))
				assert(len(titles) == 1) # didn't occur yet, would need to be handled
				law = etree.SubElement(laws, "law")
				etree.SubElement(law, "title").text = titles.pop()
				etree.SubElement(law, "filename").text = path.join(pname, name)
				kwords = etree.SubElement(law, "keywords")
				for keyword in keywords:
					etree.SubElement(kwords, "keyword").text = keyword
	xmlstr = etree.tostring(laws, pretty_print=True)
	f = open("tmp/index.xml", "w")
	f.write(xmlstr)
	f.close()

write_xml("http://www.gesetze-im-internet.de/alg/xml.zip", "alg") # contains tables
write_xml("http://www.gesetze-im-internet.de/bgb/xml.zip", "bgb")
write_xml("http://www.gesetze-im-internet.de/hgb/xml.zip", "hgb")
write_xml("http://www.gesetze-im-internet.de/gmbhg/xml.zip", "gmbhg")
write_xml("http://www.gesetze-im-internet.de/aktg/xml.zip", "aktg")
write_xml("http://www.gesetze-im-internet.de/gg/xml.zip", "gg")
#fetch()
index()
