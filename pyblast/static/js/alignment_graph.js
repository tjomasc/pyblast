var alignments = {
    create: function() {
        var width = 500, margin = {top: 20, right: 20, bottom: 20, left: 20}, barheight = 5, barpadding = 10, scoreheight = 20;
        var groups = [{name:'<40', colour: 'black'}, {name:'40-50', colour:'#1A93CD'}, {name: '50-80', colour:'#6BA405'}, {name:'80-200', colour:'#9A3CCC'}, {name: '>=200', colour:'#D80017'}]; 

        $('.alignment').each(function(i,d) {
            // Parse the table and DOM element to extract basic information 
            var from = $(this).data('query-from');
            var to = $(this).data('query-to');

            var reverse = false;
            if(from > to) {
                reverse = true;
            }

            // Parse the table, taking the header row and using to to key an object
            var data = [];
            var headers = [];
            $('table thead, table tbody', d).children('tr').each(function(i,tr) {
                if(i==0) {
                    $(tr).children('th').each(function(i,c) {
                        headers.push($(c).text());
                    });
                } else {
                    var e = {}
                    $(tr).children('td').each(function(i,c) {
                        e[headers[i]] = $(c).text();
                    });
                    data.push(e);
                }
            });
            $('table', d).hide();

            // Set basic properties for the graph
            var height = (data.length*barheight)+(data.length*barpadding)+margin.top+margin.bottom+(scoreheight*2);
            if(height > 600) {
                height = 600;
            }

            var graph = $('.alignment-graph', this);
            graph.html('');
            
            if(reverse) {
                var x = d3.scale.linear().range([width-margin.left-margin.right, 0]);
            } else {
                var x = d3.scale.linear().range([0, width-margin.left-margin.right]);
            }
            var y = d3.scale.ordinal().rangeBands([0, height-margin.top-margin.bottom-(scoreheight*2)], .5);
            var xAxis = d3.svg.axis().scale(x).orient('bottom').ticks(6);

            var svg = d3.select(graph[0]).append('svg')
                .attr('width', width)
                .attr('height', height)
                .append('g')
                .attr('transform', 'translate('+margin.left+', '+margin.top+')');

            if(reverse) {
                x.domain([to, from]);
            }else{
                x.domain([from, to]);
            }
            y.domain(data.map(function(d) { return d.Match; }));

            var scores_group = svg.append('g')
                .attr('transform', 'translate(0, '+(scoreheight/2)+')')

            scores_group.selectAll('.scores')
                .data(groups)
                .enter().append('rect')
                .attr('class', 'scores')
                .attr('x', function(d,i) { return (width-margin.left-margin.right)/groups.length*i })
                .attr('width', function(d) { return (width-margin.left-margin.right)/groups.length })
                .attr('y', 0)
                .attr('height', scoreheight)
                .attr('fill', function(d) { return d.colour; })

            scores_group.selectAll('.scores-label')
                .data(groups)
                .enter().append('text')
                .attr('class', 'scores-label')
                .attr('x', function(d,i) { return ((width-margin.left-margin.right)/groups.length*i)+margin.left })
                .attr('y', scoreheight-(scoreheight/4))
                .attr('fill', 'white')
                .text(function(d) { return d.name; })

            svg.append('text')
                .attr('y', 0)
                .text('Colour key for alignment scores')
            
            svg.append('g')
                .attr('class', 'xaxis')
                .attr('transform', 'translate(0, '+(height-margin.top-margin.bottom)+')')
                .call(xAxis);

            svg.append('g')
                .attr('transform', 'translate(0, '+(scoreheight*2)+')')
                .selectAll('.match')
                .data(data)
                .enter().append('a')
                .attr('xlink:href', function(d,i) { return '#'+d.Match; })
                .append('rect')
                .attr('class', 'match')
                .attr('x', function(d) { if(reverse) { return x(d.To) } else { return x(d.From); } })
                .attr('width', function(d) { if(reverse) { return x(d.From)-x(d.To) } else { return x(d.To)-x(d.From); } })
                .attr('y', function(d,i) { return y(d.Match); })
                .attr('height', barheight)
                .attr('fill', function(d) { 
                    var score = parseFloat(d.Score);
                    if(score < 40) {
                        return groups[0]['colour'];
                    } else if(score >= 40 && score < 50) {
                        return groups[1]['colour'];
                    } else if(score >= 50 && score < 80) {
                        return groups[2]['colour'];
                    } else if(score >= 80 && score < 200) {
                        return groups[3]['colour'];
                    } else {
                        return groups[4]['colour'];
                    }
                });
        });
    },
};
