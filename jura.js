/* Copyright 2012 C.Wilhelm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License, version 3, 
 * as published by the Free Software Foundation.
**/

// TODO: shall work for Art. 3 GG
// TODO: shall work for §22 II HGB, §24 Abs. 3 GmbHG
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

/* Paragraph/Artikel in XML finden und HTML generieren */
var find_p = function(data, paragraphs) {
	var str = "";
	$.each(paragraphs, function(i,v) {
		// console.log("//enbez[text()='§ " + v + "']");
		$.each(xp("//enbez[text()='§ " + v + "']/../../textdaten", data, data), function(j, txt) {
			str += "§ " + v + "<br />"
			str += $(txt).text()
			str += "<br/><br/>";
		});
	});
	$("#in").html(str);
};

/* Römische Zahlen finden und dersetzen, z.B. I -> Abs. 1 */
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
	$("body").html($("body").html().replace(/(Art\.|§§|§)(\W*[0-9]+\W*[IVXL]*\W*(ff\.|f\.|Abs\.|Absatz|S\.|Satz|Nr\.|Nummer)*\W*[,]?\W*)+[A-Z][A-Za-z]+/g, function(data){
		return '<span class="paragraph">' + data + '</span>';
	}));
	$(".paragraph").hover(function(){
		var p = replace_roman_letters($(this).text());
		console.log(p);
		var numbers = p.match(/[0-9]+/g);
		var names = p.match(/[A-Z][A-Za-z]+/g);
		var law = names[names.length-1].toLowerCase();
		$.get('tmp/index.xml', function(data) {
			$.each(xp("//keyword[text()='" + law + "']/../../filename", data, data), function(i, v) {
				$.get('tmp/' + $(v).text(), function(data) {
					find_p(data, numbers);
				});
			});
		});
	});
});
