var countMeal = 1;
var imgElement;

function switch_cases(flag) {
    if (flag == 0){
        //console.log("Search called me")
        $('#uploadContainer').hide();
        $('#searchContainer').show();
    }
    else{
        //console.log("Upload called me")
        $('#searchContainer').hide();
        $('#uploadContainer').show();
    }
}

function updateProgressbar(width_supplied, progressbar_id){
    $('#' + progressbar_id).width(width_supplied.toString() + '%');
}

function clearMealInputs(){
    var dishName = document.getElementById('dishName');
    var rating = document.getElementById('rating');
    dishName.value = '';
    rating.value = '';
}

function addToMealBody(){
    var tbody = document.getElementById('mealBody');
    tbody.innerHTML += '<tr id="meal-'+ countMeal +'"><td class="text-capitalize">' + $("input[name='dishName']").val() + '</td><td>' + $("input[name='rating']").val() + '</td><td><button type="button" class="custom-btn-round-small custom-btn-round-outline-dark" onclick="removeFromMeal(' + countMeal + ')">-</button></td></tr>';
    countMeal += 1;
    clearMealInputs()
}

function removeFromMeal(id){
    var tbody = document.getElementById('mealBody');
    var tr = document.getElementById('meal-' + id);
    tbody.removeChild(tr);
}

function getMealData(){
    var tbody = document.getElementById('mealBody');
    var children = tbody.children;
    var dishNames = [];
    var ratings = [];

    for (var i = 0; i < children.length; i++) {
        var tableChild = children[i];
        var trChildren = tableChild.children;
        dishNames.push(trChildren[0].innerHTML);
        ratings.push(parseInt(trChildren[1].innerHTML));
    }

    return [dishNames, ratings];
}

function createFNTemplate(dishName, nutrientsData, id){
    var newDiv = document.createElement('div');
    newDiv.className = "row align-items-center justify-content-center flavourContainer";
    var tbodyText = '';
    Object.keys(nutrientsData).forEach(function(key){
        tbodyText += '<tr class="text-capitalize"><td>' + key + '</td><td>' + nutrientsData[key][0] + '</td></tr>';
    });

    newDiv.innerHTML = '<div class="col-md-5"><div class="row align-items-center justify-content-center"><div class="col-12 custom-card"><h6>Dish name</h6><small>Showing statistics for the selected dish.</small><h1 class="text-center text-capitalize padding-all">'+ dishName + '</h1></div><div class="col-12 custom-card"><div id="flavourChart-' + id + '"></div></div></div></div><div class="col-md-5 custom-card"><h6 class="text-center">Table 2. Nutrient Information</h6><table class="table table-hover text-center"><thead class="thead-dark"><tr><th>Nutrient</th><th>Amount</th></tr></thead><tbody></tbody>' + tbodyText + '</table></div>';

    return newDiv
}

function initiliazeChart(count, flavourData){
    Highcharts.chart('flavourChart-'+count, {

        chart: {
            polar: true,
            type: 'line'
        },
    
        title: {
            text: 'Flavour Profile',
            x: -80
        },
    
        pane: {
            size: '80%'
        },
    
        xAxis: {
            categories: ['Bitter', 'Rich', 'Salt', 'Sour',
                'Sweet', 'Umami'],
            tickmarkPlacement: 'on',
            lineWidth: 0
        },
    
        yAxis: {
            gridLineInterpolation: 'polygon',
            lineWidth: 0,
            min: 0
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
            data: [flavourData['bitter'], flavourData['rich'], flavourData['salt'], flavourData['sour'], flavourData['sweet'], flavourData['umami']],
            pointPlacement: 'on'
        }]
    
    });
}

function populatePredictions(data){
    methods = ['matf', 'tfidf', 'tfidfflavour']
    for(i in methods){
        var tbody = document.getElementById('predictionsBody' + methods[i]);
        var count = 1;

        Object.keys(data[methods[i]]).forEach(function(key){
            tbody.innerHTML += '<tr data-toggle="tooltip" data-placement="right" title="' + Number(data[methods[i]][key]['rating']).toFixed(2) + '"><td>' + count + '</td><td class="text-capitalize">' + data[methods[i]][key]['dishName'] + '</td></tr>';
            count += 1
        });
    }
}

function getrecommendations(){
    var userID = parseInt(document.getElementById('userID').innerHTML);
    var form_data = new FormData();
    form_data.append('userID', userID);
    form_data.append('steps', parseInt($('input[name="steps"]').val()))
    form_data.append('floors', parseInt($('input[name="floors"]').val()))
    var currentProgress = 0;
    var progressbarID = 'progressbar';
    var speed = 200;

    progressBarinterval = setInterval(function() {
        currentProgress += 2
        updateProgressbar(currentProgress, progressbarID);
        if (currentProgress >= 98){
            clearInterval(progressBarinterval);
        }
    }, 1000);

    $.ajax({
        type        : 'POST',
        url         : '/getrecommendations',
        data        : form_data,
        dataType    : 'json',
        processData : false,
        contentType : false
    }).done(function(data) {
        console.log(data);
        populatePredictions(data);
        if (!(currentProgress >= 90)){
            clearInterval(progressBarinterval);
        }
        updateProgressbar(100, progressbarID);
        setTimeout(function(){
            $('#progressbarContainer').fadeOut(speed).next().delay(speed);
            $('#predictionsWrapper').fadeIn(speed);
            $('[data-toggle="tooltip"]').tooltip();
        }, speed + 100);
    });
}

function resetImageContainer(){
    var formBody = document.getElementById('mealForm');
    formBody.innerHTML = '<center><button type="button" class="custom-btn custom-btn-outline-dark rounded-button" id="submitMealImage">Done</button></center>'
    var canvasElement = document.getElementById('imageContainer');
    var context = canvasElement.getContext('2d');
    context.clearRect(0, 0, canvasElement.width, canvasElement.height);
    $('#imageWrapper').hide();
}

function resetProgressBar(id, speed){
    updateProgressbar(0, id);
    $('#progressbarContainer').fadeIn(speed);
}

function resetPredictions(speed){
    $('#predictionsWrapper').fadeOut(speed).next().delay(speed);
    methods = ['matf', 'tfidf', 'tfidfflavour'];
    for(i in methods){
        var tbody = document.getElementById('predictionsBody' + methods[i]);
        tbody.innerHTML = ''
    }

}

function resetFlavourContainers(){
    try {
        $('.flavourContainer').remove();
    }
    catch(err){
        console.log(err);
    }
}

function resetForm(){
    var mealBody = document.getElementById('mealBody');
    mealBody.innerHTML = ''
}

function getRetrainedPredictions(){
    var form_data = new FormData();
    form_data.append('userID', parseInt(document.getElementById('userID').innerHTML));
    form_data.append('steps', parseInt($('input[name="steps"]').val()))
    form_data.append('floors', parseInt($('input[name="floors"]').val()))
    var progressbarID = 'progressbar';
    var speed = 200;
    var currentProgress = 0;

    resetPredictions(speed);
    resetProgressBar(progressbarID, speed);

    progressBarinterval = setInterval(function() {
        currentProgress += 1
        updateProgressbar(currentProgress, progressbarID);
        if (currentProgress >= 98){
            clearInterval(progressBarinterval);
        }
    }, 1000);
    
    $.ajax({
        type        : 'POST',
        url         : '/retrain',
        data        : form_data,
        dataType    : 'json',
        processData : false,
        contentType : false
    }).done(function(data) {
        console.log(data);
        populatePredictions(data);
        if (!(currentProgress >= 90)){
            clearInterval(progressBarinterval);
        }
        updateProgressbar(100, progressbarID);
        setTimeout(function(){
            $('#progressbarContainer').fadeOut(speed).next().delay(speed);
            $('#predictionsWrapper').fadeIn(speed);
            $('[data-toggle="tooltip"]').tooltip();
        }, speed + 100);
    });
}

function autocomplete(inp, arr) {
    var currentFocus;
    inp.addEventListener("input", function(e) {
        var a, b, i, val = this.value;
        closeAllLists();
        if (!val) { return false;}
        currentFocus = -1;
        a = document.createElement("DIV");
        a.setAttribute("id", this.id + "autocomplete-list");
        a.setAttribute("class", "autocomplete-items");
        a.style.width = inp.offsetWidth + 'px'
        this.parentNode.insertBefore(a, inp.nextSibling)
        for (i = 0; i < arr.length; i++) {
            if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
                b = document.createElement("DIV");
                b.className = "text-capitalize"
                b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
                b.innerHTML += arr[i].substr(val.length);
                b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
                b.addEventListener("click", function(e) {
                    inp.value = this.getElementsByTagName("input")[0].value;
                    closeAllLists();
                });
                a.appendChild(b);
            }
        }
    });
    inp.addEventListener("keydown", function(e) {
        var x = document.getElementById(this.id + "autocomplete-list");
        if (x) x = x.getElementsByTagName("div");
        if (e.keyCode == 40) {
            currentFocus++;
            addActive(x);
        } else if (e.keyCode == 38) {
            currentFocus--;
            addActive(x);
        } else if (e.keyCode == 13) {
            e.preventDefault();
            if (currentFocus > -1) {
                if (x) x[currentFocus].click();
            }
        }
    });
    function addActive(x) {
        if (!x) return false;
        removeActive(x);
        if (currentFocus >= x.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = (x.length - 1);
        x[currentFocus].classList.add("autocomplete-active");
    }
    function removeActive(x) {
        for (var i = 0; i < x.length; i++) {
            x[i].classList.remove("autocomplete-active");
        }
    }
    function closeAllLists(elmnt) {
        var x = document.getElementsByClassName("autocomplete-items");
        for (var i = 0; i < x.length; i++) {
            if (elmnt != x[i] && elmnt != inp) {
                x[i].parentNode.removeChild(x[i]);
            }
        }
    }
    document.addEventListener("click", function (e) {
            closeAllLists(e.target);
    });
}

function drawImageOnCanvas(){
    var canvasElement = document.getElementById('imageContainer');
    var context = canvasElement.getContext('2d');
    context.lineWidth = 5;
    context.strokeStyle = "#FFFFFF"
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

function sendMeal(counter){
    var form_data = new FormData();
    var dishNames = [];
    var ratings = [];
    var choice = 'search';

    for(var i = 1; i < counter; i++){
        if ($("select[name='dish-" + i + "']").val() != 'none'){
            dishNames.push($("select[name='dish-" + i + "']").val());
            ratings.push(parseInt($("input[name='rating-" + i + "']").val()));
        }
    }

    form_data.append('choiceRadio', choice);
    form_data.append('userID', parseInt(document.getElementById('userID').innerHTML));
    form_data.append('dishNames', dishNames.toString());
    form_data.append('ratings', ratings.toString());

    $.ajax({
        type        : 'POST',
        url         : '/workflow',
        data        : form_data,
        dataType    : 'json',
        processData : false,
        contentType : false
    }).done(function(data){
        var predictionsContainer = document.getElementById('predictionsContainer');
        count = 1
        resetForm();
        resetFlavourContainers();
        resetProgressBar();
        resetPredictions();

        Object.keys(data).forEach(function(key){
                
            var newDiv = createFNTemplate(key, data[key]['nutrientsData'], count);
            predictionsContainer.parentNode.insertBefore(newDiv, predictionsContainer);
            initiliazeChart(count, data[key]['flavourData']);
            count += 1;
        });
        getRetrainedPredictions();
    });
}

function setup(){
    console.log("Setting up...");
    var dishes =  ["curried green bean salad", "keema aloo", "paratha", "black chana with potato", "tomato cucumber kachumbar"];
    autocomplete(document.getElementById("dishName"), dishes);
    getrecommendations();

    $('form').submit(function(event) {
        event.preventDefault();
    });
    
    $('#submitMeal').on('click', function() {

        var form_data = new FormData();
        var file_data = $('#uploadDish').prop('files')[0]; 
        var retVal = getMealData();
        var choice = $("input[name='choiceRadio']:checked").val();
        form_data.append('choiceRadio', choice);
        form_data.append('userID', parseInt(document.getElementById('userID').innerHTML));
        form_data.append('dishNames', retVal[0].toString());
        form_data.append('ratings', retVal[1].toString());
        form_data.append('uploadDish', file_data);

        $.ajax({
            type        : 'POST',
            url         : '/workflow',
            data        : form_data,
            dataType    : 'json',
            processData : false,
            contentType : false
        }).done(function(data) {
            var predictionsContainer = document.getElementById('predictionsContainer');
            count = 1;
            if (choice=='search'){
                resetForm();
                resetFlavourContainers();
                resetImageContainer();
                resetProgressBar();
                resetPredictions();
                Object.keys(data).forEach(function(key){
                
                    var newDiv = createFNTemplate(key, data[key]['nutrientsData'], count);
                    predictionsContainer.parentNode.insertBefore(newDiv, predictionsContainer);
                    initiliazeChart(count, data[key]['flavourData']);
                    count += 1;
                });
                getRetrainedPredictions();
            }
            else {
                resetForm();
                resetImageContainer();
                resetFlavourContainers();
                resetPredictions();
                x = data['predictions'];
                imgElement = new Image();
                imgElement.onload = drawImageOnCanvas;
                imgElement.src = data['filename'];
                var mealBodyButton = document.getElementById('submitMealImage');
                var counter = 1;
                for(i in data['predictions']){
                    key = Object.keys(data['predictions'][i])[0]
                    lst = data['predictions'][i][key];
                    option_text = '';
                    for(i in lst){
                        option_text += '<option class="text-capitalize" value="' + Object.keys(lst[i])[0] + '">' + Object.keys(lst[i])[0] + '</option>';
                    }
                    option_text += '<option class="text-capitalize">none</option>';
                    div = document.createElement('div');
                    div.className = "form-group";
                    coordinates = key.split(',');
                    for(i in coordinates){
                        coordinates[i] = parseInt(coordinates[i]);
                    }
                    form_group_text = '<div class="row align-items-center" onmouseover=drawBoundingBox(' + coordinates[0]/2 + ',' + coordinates[1]/2 + ',' + coordinates[2]/2 + ','+ coordinates[3]/2 +  ') onmouseout="removeBoundingBox()"><div class="col-6"><label for="dish-' + counter + '">Dish ' + counter + '</label><select class="form-control text-capitalize" name="dish-' + counter + '" id="dish-' + counter + '">' + option_text + '</select></div><div class="col-6"><label for="rating-' + counter + '">Rating</label><input type="number" class="form-control text-capitalize" id="rating-' + counter + '" name="rating-' + counter + '"></div></div>';
                    div.innerHTML = form_group_text;
                    mealBodyButton.parentNode.parentNode.insertBefore(div, mealBodyButton.parentNode);
                    counter += 1;
                }
                mealBodyButton.onclick = function() {
                    sendMeal(counter);
                }
                $('#imageWrapper').show();
            }
            
        });
    });
}