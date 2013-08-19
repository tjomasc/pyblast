$(document).ready(function(){var e={align:function(){var e=500,t={top:20,right:20,bottom:20,left:20},n=5,r=10,i=20,s=[{name:"<40",colour:"black"},{name:"40-50",colour:"#1A93CD"},{name:"50-80",colour:"#6BA405"},{name:"80-200",colour:"#9A3CCC"},{name:">=200",colour:"#D80017"}];$(".alignment").each(function(o,u){var a=$(this).data("query-from"),f=$(this).data("query-to"),l=!1;a>f&&(l=!0);var c=[],h=[];$("table thead, table tbody",u).children("tr").each(function(e,t){if(e==0)$(t).children("th").each(function(e,t){h.push($(t).text())});else{var n={};$(t).children("td").each(function(e,t){n[h[e]]=$(t).text()});c.push(n)}});$("table",u).hide();var p=c.length*n+c.length*r+t.top+t.bottom+i*2;p>600&&(p=600);var d=$(".alignment-graph",this);if(l)var v=d3.scale.linear().range([e-t.left-t.right,0]);else var v=d3.scale.linear().range([0,e-t.left-t.right]);var m=d3.scale.ordinal().rangeBands([0,p-t.top-t.bottom-i*2],.5),g=d3.svg.axis().scale(v).orient("bottom").ticks(6),y=d3.select(d[0]).append("svg").attr("width",e).attr("height",p).append("g").attr("transform","translate("+t.left+", "+t.top+")");l?v.domain([f,a]):v.domain([a,f]);m.domain(c.map(function(e){return e.Match}));var b=y.append("g").attr("transform","translate(0, "+i/2+")");b.selectAll(".scores").data(s).enter().append("rect").attr("class","scores").attr("x",function(n,r){return(e-t.left-t.right)/s.length*r}).attr("width",function(n){return(e-t.left-t.right)/s.length}).attr("y",0).attr("height",i).attr("fill",function(e){return e.colour});b.selectAll(".scores-label").data(s).enter().append("text").attr("class","scores-label").attr("x",function(n,r){return(e-t.left-t.right)/s.length*r+t.left}).attr("y",i-i/4).attr("fill","white").text(function(e){return e.name});y.append("text").attr("y",0).text("Colour key for alignment scores");y.append("g").attr("class","xaxis").attr("transform","translate(0, "+(p-t.top-t.bottom)+")").call(g);y.append("g").attr("transform","translate(0, "+i*2+")").selectAll(".match").data(c).enter().append("a").attr("xlink:href",function(e,t){return"#"+e.Match}).append("rect").attr("class","match").attr("x",function(e){return l?v(e.To):v(e.From)}).attr("width",function(e){return l?v(e.From)-v(e.To):v(e.To)-v(e.From)}).attr("y",function(e,t){return m(e.Match)}).attr("height",n).attr("fill",function(e){var t=parseFloat(e.Score);return t<40?s[0].colour:t>=40&&t<50?s[1].colour:t>=50&&t<80?s[2].colour:t>=80&&t<200?s[3].colour:s[4].colour})})}}});