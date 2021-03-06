/* Copyright 2012 C.Wilhelm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License, version 3, 
 * as published by the Free Software Foundation.
**/

// TODO: handle §21 f. BGB, Art. 9ff. GG (e.g. "show next"- Button (APPEND))

/* jQuery XPath wrapper based on a script written by John Firebaugh, see https://github.com/jfirebaugh/jquery-xpath */
var xp = function(xpath, contextNode, rootDocument) {
	if (!rootDocument) rootDocument = document;
	var iterator = rootDocument.evaluate(xpath, contextNode, null, XPathResult.ANY_TYPE, null);
	var item, nodes = [];
	while (item = iterator.iterateNext())
		nodes.push(item);
	return nodes;
};
(function($) {
	$.xpath = function(xpath) {
		return $(xp(xpath, document));
	}
	$.fn.xpath = function(xpath) {
		var nodes = [];
		this.each(function() {
			nodes.push.apply(nodes, xp(xpath, this));
		});
		return this.pushStack(nodes, "xpath", xpath);
	}
})(jQuery);

/* Römische Zahlen finden und ersetzen, z.B. I -> Abs. 1 */
function deromanize(roman) {
	// source: http://blog.stevenlevithan.com/archives/javascript-roman-numeral-converter
	var roman = roman.toUpperCase();
	var lookup = {I:1,V:5,X:10,L:50,C:100,D:500,M:1000};
	var arabic = 0, i = roman.length;
	while (i--) {
		if(lookup[roman[i]] < lookup[roman[i+1]])
			arabic -= lookup[roman[i]];
		else
			arabic += lookup[roman[i]];
	}
	return arabic;
}
var replace_roman_letters = function (str) {
	return str.replace(/[IVXL]+/g, function(data){
		return 'Abs.' + deromanize(data);
	})
};

/* veranlassen, dass die entsprechenden Paragraphen angezeigt werden, wenn Maus über ein Gesetzes-Zitat fährt */
jQuery(document).ready(function($) {
	if(!$("#in").length) $("body").html('<div id="in" style="border-style:solid;border-width:1px;float:right;height:100%;width:30%;overflow:auto;"></div>' + $("body").html());
	$("body").html($("body").html().replace(/(Art|§§|§)(\W*[0-9]+\W*[IVXL]*\W*(ff|f|Abs|Absatz|S|Satz|Nr|Nummer|Buchst|lit|Buchstabe)*\W*[,]?\W*)+[A-Z][A-Za-z]+/g, function(data){
		//console.log(data);
		return '<span class="paragraph">' + data + '</span>';
	}));
	$(".paragraph").hover(function(){
		var txt = replace_roman_letters($(this).text());
		var namen = txt.match(/[A-Z][A-Za-z]+/g);
		var gesetz = namen[namen.length-1];
		var paragraphen = [];
		$.each(txt.split(","), function(i, p) {
			var paragraph = {paragraph:null, absatz: null, satz: null, nummer: null, buchstabe: null, folgende: false, istartikel: false};
			p = p.replace(/(Art|§§|§)/, function(str){
				paragraph.istartikel = str.search("Art") != -1;
				return '';
			});
			p = p.replace(/(Abs|Absatz)\W*[0-9]+/, function(str){
				paragraph.absatz = str.match(/[0-9]+/)[0];
				return '';
			});
			p = p.replace(/(S|Satz)\W*[0-9]+/, function(str){
				paragraph.satz = str.match(/[0-9]+/)[0];
				return '';
			});
			p = p.replace(/(Nr|Nummer)\W*[0-9]+/, function(str){
				paragraph.nummer = str.match(/[0-9]+/)[0];
				return '';
			});
			p = p.replace(/(Buchst|lit|Buchstabe)\W*[0-9]+/, function(str){
				paragraph.buchstabe = str.match(/[0-9]+/)[0];
				return '';
			});
			paragraph.paragraph = p.match(/[0-9]+/)[0];
			paragraph.folgende = /ff|f/.test(p);
			paragraphen.push(paragraph);
			//console.log(p, paragraph); // there shouldn't be much left
		});
		$.get('tmp/index.xml', function(data) {
			$.each(xp("//keyword[text()='" + gesetz.toLowerCase() + "']/../..", data, data), function(i, law) {
				var filename = xp("./filename", law, data);
				var title = xp("./title", law, data);
				$.get('tmp/' + $(filename).text(), function(data) {
					find_p(data, paragraphen, $(title).text());
				});
			});
		});
	});
});

/* replacement for (new XMLSerializer()).serializeToString(txt) */
var serialize = function(node) {
	if(node.textContent === undefined) str = "";
	else str = "<"+node.tagName+">"+node.textContent+"</"+node.tagName+">\n";
	$.each($(node).children(), function(i,c) {
		str += serialize(c);
	});
	return str;
}

/* Paragraph/Artikel in XML finden und HTML generieren */
var find_p = function(data, paragraphs, law_name) {
	var str = "<h2>" + law_name + "</h2>";
	var s = new XMLSerializer();  
	$.each(paragraphs, function(i,p) {
		if(p.istartikel) begstr = "Art "; else begstr = "§ ";
		elem = xp("//enbez[text()='" + begstr + p.paragraph + "']", data, data)[0]
		str += "<h3>";
		str += begstr + p.paragraph;
		title = $(xp("../titel", elem, data)).text();
		if(title != "") str += "&nbsp;&nbsp;" + title;
		str += "</h3>";
		txt = xp("../../textdaten/text/Content", elem, data);
		txt = serialize(txt);
		str += txt + "<br/><br/>";
	});
	$("#in").html(str);
};
