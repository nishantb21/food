var socket = io();
var currentProgress = 0;
var progressBarinterval;
var speed = 200;
var imgElement;
var dishIndexArray = [];
var mapping = [];
var dishName;

function updateProgressbar(width_supplied){
    $('#progressbar').width(width_supplied.toString() + '%');
}

function updateProgressbar2(width_supplied){
    $('#progressbar2').width(width_supplied.toString() + '%');
}

function drawImageOnCanvas(){
    var canvasElement = document.getElementById('imageContainer');
    var context = canvasElement.getContext('2d');
    context.drawImage(this, 0, 0, 400, 400);
}

function drawBoundingBox(xmin, ymin, xmax, ymax){
    var canvasElement = document.getElementById('imageContainer');
    var context = canvasElement.getContext('2d');
    context.beginPath();
    context.moveTo(xmin, ymin);
    context.lineTo(xmin, ymax);
    context.lineTo(xmax, ymax);
    context.lineTo(xmax, ymin);
    context.lineTo(xmin, ymin);
    context.stroke();
}

function removeBoundingBox(){
    var canvasElement = document.getElementById('imageContainer');
    var context = canvasElement.getContext('2d');
    context.clearRect(0, 0, canvasElement.width, canvasElement.height);
    context.drawImage(imgElement, 0, 0, 400, 400);
}

function appendtoArray(index){

    $('#' + index.toString()).prop('checked', !($('#' + index.toString()).prop('checked')));
    // if (index in dishIndexArray){
    //     dishIndexArray.pop(dishIndexArray.indexOf(index));
    // }
    // else {
    //     dishIndexArray.push(index);
    // }
    dishName = mapping[index];
}

function callWorkflow(){
    // var dishNameArray = [];
    // dishIndexArray.forEach(function(index){
    //     dishNameArray.push(mapping[index]);
    // });
    // console.log(dishNameArray);
    var info = document.getElementById('information').innerHTML.split(',');
    var userID = parseInt(info[0]);
    var rating = parseInt(info[1]);

    var dishNameElement = document.getElementById('dishNameHeading');
    dishNameElement.innerHTML = dishName;

    updateProgressbar2(0);

    $('#workflowContainer').fadeOut(speed).next().delay(speed);
    $('#progressbarWrapper').fadeIn(speed);

    progressBarinterval = setInterval(function() {
        currentProgress += 10
        updateProgressbar2(currentProgress);
        if (currentProgress >= 90){
            clearInterval(progressBarinterval);
        }
    }, 1000);

    $.ajax({
        type: "POST",
        url: '/workflow',
        data: {
            dishName: dishName,
            userID: userID,
            rating: rating
        }
    });
}

$(function(){
    progressBarinterval = setInterval(function() {
        currentProgress += 10
        updateProgressbar(currentProgress);
        if (currentProgress >= 90){
            clearInterval(progressBarinterval);
        }
    }, 1000);
});

socket.on('image', function(data){
    console.log(data);
    imgElement = new Image();
    imgElement.onload = drawImageOnCanvas;
    imgElement.src = data['path'];

    Object.keys(data['recognitionData']).forEach(function(key){
        coordinates = data['recognitionData'][key]['coordinates'];
        mapping.push(key);
        row = '<div class="custom-control custom-radio"><input type="radio" class="custom-control-input" id="' + mapping.indexOf(key) + '" name="dishName" value="' + key + '"><label class="custom-control-label" onclick="appendtoArray(' + mapping.indexOf(key) + ')">' + key + '</div>';
        
        recognitionResults.innerHTML += '<tr onmouseover=drawBoundingBox(' + coordinates[0]/2 + ',' + coordinates[1]/2 + ',' + coordinates[2]/2 + ','+ coordinates[3]/2 +  ') onmouseout=removeBoundingBox() ><td>' + row + '</td></tr>';
    });
    if (!(currentProgress >= 90)){
        clearInterval(progressBarinterval);
    }
    updateProgressbar(100);
    setTimeout(function(){
        $('#progressbarContainer').fadeOut(speed).next().delay(speed);
        $('#recognitionContainer').fadeIn(speed);
    }, speed + 100);

});

socket.on('flavourData', function(data){
    var myChart = Highcharts.chart('flavourChart',{
        chart: {
            polar: true,
            type: 'line',
        },
    
        title: {
            text: 'Flavour Profile',
            x: -80
        },
    
        pane: {
            size: '80%'
        },
    
        xAxis: {
            categories: ['Rich', 'Salty', 'Sweet'],
            tickmarkPlacement: 'on',
            lineWidth: 0
        },
    
        yAxis: {
            gridLineInterpolation: 'polygon',
            lineWidth: 0,
            min: 0,
            max: 5
        },
    
        tooltip: {
            shared: true,
            pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y}</b><br/>'
        },
    
        legend: {
            align: 'right',
            verticalAlign: 'top',
            y: 70,
            layout: 'vertical'
        },
    
        series: [{
            name: 'Score',
            data: [data.flavourData['rich'], data.flavourData['salt'], data.flavourData['sweet']],
            pointPlacement: 'on'
        }]
    });
});

socket.on('predictions', function(data){
    var tbody = document.getElementById('predictionsBody');
    var count = 1;

    Object.keys(data.predictions).forEach(function(key){
        tbody.innerHTML += '<tr><td>' + count + '</td><td>' + data.predictions[key]['dish_name'] + '</td><td>' + data.predictions[key]['rating'] + '</td></tr>';
        count += 1
    });

    if (!(currentProgress >= 90)){
        clearInterval(progressBarinterval);
    }
    updateProgressbar(100);
    setTimeout(function(){
        $('#progressbarContainer').fadeOut(speed).next().delay(speed);
        $('#predictionsContainer').fadeIn(speed);
    }, speed + 100);
    

});

socket.on('workflow', function(data){
    
    var nutrientsBody = document.getElementById('nutrientBody');
    nutrientsBody.innerHTML = '';

    Object.keys(data['nutrientData']).forEach(function(key){
        nutrientsBody.innerHTML += '<tr><td>' + key + '</td><td>' + data['nutrientData'][key][0] + '</td></tr>';
    });

    var myChart = Highcharts.chart('flavourChart',{
        chart: {
            polar: true,
            type: 'line',
        },
    
        title: {
            text: 'Flavour Profile',
            x: -80
        },
    
        pane: {
            size: '80%'
        },
    
        xAxis: {
            categories: ['Rich', 'Salty', 'Sweet'],
            tickmarkPlacement: 'on',
            lineWidth: 0
        },
    
        yAxis: {
            gridLineInterpolation: 'polygon',
            lineWidth: 0,
            min: 0,
            max: 5
        },
    
        tooltip: {
            shared: true,
            pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y}</b><br/>'
        },
    
        legend: {
            align: 'right',
            verticalAlign: 'top',
            y: 70,
            layout: 'vertical'
        },
    
        series: [{
            name: 'Score',
            data: [data.flavourData['rich'], data.flavourData['salt'], data.flavourData['sweet']],
            pointPlacement: 'on'
        }]
    });

    var tbody = document.getElementById('predictionsBody');
    tbody.innerHTML = '';
    var count = 1;

    Object.keys(data.predictions).forEach(function(key){
        tbody.innerHTML += '<tr><td>' + count + '</td><td>' + data.predictions[key]['dish_name'] + '</td><td>' + data.predictions[key]['rating'] + '</td></tr>';
        count += 1
    });

    if (!(currentProgress >= 90)){
        clearInterval(progressBarinterval);
    }
    updateProgressbar2(100);
    setTimeout(function(){
        $('#progressbarWrapper').fadeOut(speed).next().delay(speed);
        $('#workflowContainer').fadeIn(speed);
    }, speed + 100);

});

