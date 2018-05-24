$(function (jsondata) {
    $('#container').highcharts({
               chart: {
            renderTo: 'container',
            type: 'scatter',
            zoomType: 'xy'
        },
        plotOptions: {
            scatter: {
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 2
                    }
                }
            }
        },
        series: [{
        		color: 'rgba(119, 152, 191, .5)',
            data: [
                {x: 0, y: 0, marker: { enabled: false } },
                [0, 51.6],
                null,
                {x: 1, y: 0, marker: { enabled: false} },
                [1, 59.0],
                null,
                {x: 2, y: 0, marker: { enabled: false } },
                [2, 49.2]
            ]
        },
        {
        color: 'rgba(223, 83, 83, .5)',
            data: [
                {x: 0, y: 0, marker: { enabled: false } },
                [0, -51.6],
                null,
                {x: 1, y: 0, marker: { enabled: false} },
                [1, -59.0],
                null,
                {x: 2, y: 0, marker: { enabled: false } },
                [2, -49.2]
            ]
        }

        ]


    });
});


$(function (jsondata) {
    $('#container').highcharts({
               chart: {
            renderTo: 'container',
            type: 'scatter',
            zoomType: 'xy'
        },
        plotOptions: {
            scatter: {
                lineWidth: 1,
                states: {
                    hover: {
                        lineWidth: 2
                    }
                }
            }
        },
        series: [{
        		color: 'rgba(119, 152, 191, .5)',
            data: [
                {x: 0, y: 0, marker: { enabled: false } },
                [0, 51.6],
                null,
                {x: 1, y: 0, marker: { enabled: false} },
                [1, 59.0],
                null,
                {x: 2, y: 0, marker: { enabled: false } },
                [2, 49.2]
            ]
        },
        {
        color: 'rgba(223, 83, 83, .5)',
            data: [
                {x: 0, y: 0, marker: { enabled: false } },
                [0, -51.6],
                null,
                {x: 1, y: 0, marker: { enabled: false} },
                [1, -59.0],
                null,
                {x: 2, y: 0, marker: { enabled: false } },
                [2, -49.2]
            ]
        }

        ]


    });
});