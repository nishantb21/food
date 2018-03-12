var socket = io();
socket.on('prediction', function(data){
  var i = 1;
  var parser = JSON.parse(data.replace(/'/g, "\""));
  $.each(parser, function(k,v){
    $('#label'+i.toString()).html('<input type="radio" name="food" id="option'+i+'" value="'+k+'" autocomplete="off">'+k);
    i++;
  });
  $('#predictions').fadeIn();
  $('#predSelection').click(function(){
    $.post("/food",{
      dish: $('input[type=radio]:checked').val()
    },
    function(data, status){
      console.log(data,status);
    });
  });
});
socket.on('flavors',function(data){
  console.log(data);
  $('#flavor').fadeIn();
  loadFlavorChart(data);
});

socket.on('recommendations',function(data){
  $('#recoLoader').fadeOut();
  $('#recommendations').fadeIn();
  var parser = JSON.parse(data);
  for(var i=0;parser.predicted_rating_list.length;i++){
    var dishName = parser.predicted_rating_list[i].dish_name;
    var ratings = parser.predicted_rating_list[i].rating;
    $('#recoTableBody').append('<tr><td>'+dishName+'</td><td>'+ratings+'</td></tr>');
  }
});
function loadFlavorChart(data){
  dataParser = JSON.parse(data.flavor);
  var labels = [];
  var values = [];
  $.each(dataParser, function(k,v){
    labels.push(k);
    values.push(v);
  });


  var myChart = Highcharts.chart('flavorChart',{
    chart: {
      polar: true,
      type: 'line'
    },
    title: {
      text: 'Flavor scores for '+data.dishName,
      x: -40
    },
    pane: {
      startAngle: 0,
      endAngle: 360
    },
    xAxis: {
      categories: labels,
      tickmarkPlacement: 'on',
      lineWidth: 0,
      style:{
        fontSize: '30px'
      }
    },
    yAxis: {
      gridLineInterpolation: 'polygon',
      lineWidth: 0,
      min: 0
    },
   legend: {
       align: 'right',
       verticalAlign: 'top',
       y: 70,
       layout: 'vertical'
   },
   series: [{
     name: 'Score',
     data: values,
     pointPlacement: 'on'
   }]
 });

}
socket.on('recommendations',function(data){
  console.log(data);
});
