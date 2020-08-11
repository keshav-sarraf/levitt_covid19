console.log("Landing Page.JS Called");

var casesChart = null;
var casesCtx = document.getElementById('casesChart').getContext('2d');

var levittChart = null;
var levittCtx = document.getElementById('levittChart').getContext('2d');

var fittedChart = null;
var fittedCurvectx = document.getElementById('fittedCurveChart').getContext('2d');

var selectedLocation = "india";

function createCasesChart(input){
    casesChart = new Chart(casesCtx, {
        type: 'line',
        data: {
            labels: input["dates"],
            datasets: [{
                label: 'Confirmed',
                data: input.totalconfirmed,
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1,
                fill: false,
            },
            {
                label: 'Recovered',
                data: input.totalrecovered,
                backgroundColor: 'green',
                borderColor: 'green',
                borderWidth: 1,
                fill: false,
            },
            {
                label: 'Deceased',
                data: input.totaldeceased,
                backgroundColor: 'red',
                borderColor: 'red',
                borderWidth: 1,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Cumulative cases till date'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'date'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    },
                    ticks: {
                        callback: formatYAxis
                    }
                }]
            }
        }
    });
}

function createLevittChart(input){
    levittChart = new Chart(levittCtx, {
        type: 'line',
        data: {
            labels: input["dates"],
            datasets: [{
                label: 'Levitt',
                data: input.levitt_score,
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Levitt Score'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'date'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    });
}

function createFittedChart(input){
    fittedChart = new Chart(fittedCurvectx, {
        type: 'line',
        data: {
            labels: input["dates"],
            datasets: [{
                label: 'Levitt Score',
                data: input.levitt_score,
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1,
                fill: false,
            },
            {
                label: 'Fitted Curve',
                data: input.linear_fit,
                backgroundColor: 'orange',
                borderColor: 'orange',
                borderWidth: 1,
                fill: false,
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: 'Levitt Score'
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'date'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: 'Value'
                    }
                }]
            }
        }
    });
}

function updateCasesChart(input){

    casesChart.data.labels = input["dates"];

    casesChart.data.datasets = [{
                label: 'Confirmed',
                data: input.totalconfirmed,
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1,
                fill: false,
            },
            {
                label: 'Recovered',
                data: input.totalrecovered,
                backgroundColor: 'green',
                borderColor: 'green',
                borderWidth: 1,
                fill: false,
            },
            {
                label: 'Deceased',
                data: input.totaldeceased,
                backgroundColor: 'red',
                borderColor: 'red',
                borderWidth: 1,
                fill: false,
            }];

    casesChart.update();
    console.log("update done");

}

function updateLevittChart(input){
    levittChart.data.labels = input["dates"];

    levittChart.data.datasets = [{
                label: 'Levitt',
                data: input.levitt_score,
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1,
                fill: false,
            }];

    levittChart.update();
}

function updateFittedChart(input){

    fittedChart.data.labels = input["dates"];

    fittedChart.data.datasets = [{
                label: 'Levitt Score',
                data: input.levitt_score,
                backgroundColor: 'blue',
                borderColor: 'blue',
                borderWidth: 1,
                fill: false,
            },
            {
                label: 'Fitted Curve',
                data: input.linear_fit,
                backgroundColor: 'orange',
                borderColor: 'orange',
                borderWidth: 1,
                fill: false,
            }];

    fittedChart.update();
}

function displayCasesChart(data){
    console.log("display cases chart");
    if(casesChart == null){
        createCasesChart(data);
    } else{
        updateCasesChart(data);
    }
}

function displayLevittChart(data){
    if(levittChart == null){
        createLevittChart(data);
    } else {
        updateLevittChart(data);
    }
}

function displayFittedCurve(data){
    if(fittedChart == null){
        createFittedChart(data);
    } else {
        updateFittedChart(data);
    }

    //TODO: fix the spaghetti code... initialize it to null somewhere
    let numDaysEstimated = data.num_days_estimated != null ? data.num_days_estimated : "> an year :(";

    $("#numDaysEstimated").html(numDaysEstimated);
}

function fetchCasesData(location){
    console.log("fetching cases " + location);
    $.get("/api/cases/" + location, function(data){
        displayCasesChart(data);
    });
}

function fetchLevittData(location){
    $.get("/api/levitt/" + location, function(data){
        displayLevittChart(data);
    });
}

function fetchFittedCurve(numPastDays, location){
    url = "/api/levitt/fit/" + location + "/" + numPastDays;
    console.log(url);
    $.get(url, function(data){
        displayFittedCurve(data);
    });
}

function updatePageOnLocationChange(location){
    console.log(location);

    fetchCasesData(location);
    fetchLevittData(location);
}

fetchCasesData("india");
fetchLevittData("india");


//range picker code
const $valueSpan = $('.valueSpan2');
const $value = $('#daysRangePicker');
$valueSpan.html($value.val());
$value.on('input change', () => {
    $valueSpan.html($value.val());
});

//curve fit btn click
$("#curvefitBtn").click(function(){
  //fetch data
  numPastDays = $value.val();
  fetchFittedCurve(numPastDays, selectedLocation);
});

//autocomplete
$('.basicAutoComplete').autoComplete({
    resolverSettings: {
        url: '/api/locations'
    }
});

//on selection
$('.basicAutoComplete').on('autocomplete.select', function (evt, item) {
    console.log("item selected - " + item);
    updatePageOnLocationChange(item);
    selectedLocation = item;

    if(fittedChart != null){
        fittedChart.destroy();
        fittedChart = null;
    }

    $("#numDaysEstimated").html("-");
});

//convert to lakhs
function formatYAxis(value) {
    var ranges = [
        { divider: 1e7, suffix: 'C' },
        { divider: 1e5, suffix: 'L' },
        { divider: 1e3, suffix: 'k' }
    ];

    function formatNumber(n) {
        for (var i = 0; i < ranges.length; i++) {
            if (n >= ranges[i].divider) {
            return (n / ranges[i].divider).toString() + ranges[i].suffix;
        }
    }
    return n;
 }
 return formatNumber(value);
}
