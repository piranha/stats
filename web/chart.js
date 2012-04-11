window.addEventListener('load', main);

function main() {
    var chart = d3.select('body')
        .append('svg')
        .attr('class', 'chart');

    d3.json('web/ways.json', function(data) {
        var label;

        data = data
            .filter(function(d) { return d.railways !== undefined; })
            .sort(function(a, b) { return b.railways - a.railways; })
            .slice(0, 20);

        var x = d3.scale.linear()
            .domain([0, data.length - 1])
            .range([0, 1000]);
        var y = d3.scale.linear()
            .domain([d3.min(data, function(d) { return d.railways; }),
                     d3.max(data, function(d) { return d.railways; })])
            .range([200, 0]);

        xAxis = d3.svg.axis()
            .scale(x)
            .ticks(19)
            .tickFormat(function(i) {
                return data[i].name;
            });
        var yAxis = d3.svg.axis()
            .scale(y)
            .orient('right')
            .ticks(10);

        var line = d3.svg.line()
            .x(function(d, i) {
                return x(i);
            })
            .y(function(d) {
                return y(d.railways);
            });

        chart.append('svg:g').call(xAxis);
        chart.append('svg:g').call(yAxis);
        chart.append('svg:path').attr('d', line(data));

        var circles = chart.append('svg:g').selectAll('.data-point').data(data).enter()
            .append('svg:circle')
            .attr('class', 'data-point')
            .attr('cx', function(d, i) {
                return x(i);
            })
            .attr('cy', function(d) {
                return y(d.railways);
            })
            .attr('r', 4);

        circles
            .on('mouseover', function(d) {
                label.text(d.name + ': ' + d.railways + ' km');
            })
            .on('mouseout', function() {
                label.text('');
            });

        label = chart.append('svg:text')
            .attr('x', 1000)
            .attr('y', 200);
    });
}
