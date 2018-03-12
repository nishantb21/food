var express = require('express');
var app = express();
var fileUpload = require('express-fileupload');
var port = process.env.PORT || 3000;
var server = require('http').createServer(app);
var uuidv4 = require('uuid/v4');
var myParser = require("body-parser");
var io = require('socket.io')(server);
var spawn = require("child_process").spawn;
var conn = []
app.use(fileUpload());
app.use("/", express.static(__dirname+'/'));
app.use(myParser.urlencoded({extended: true}));
app.set('view engine', 'ejs');

var rating;
var userID;

server.listen(port, function () {
  console.log('Server listening at port ' + port);
});

app.get('/',function(req,res){
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', function(socket){
  // Some demo.html just connected
})

app.post('/upload',function(req,res){
  if(!req.files)
    return res.status(400).send('No files were uploaded');
  var img = req.files.img;
  rating = req.body.rating;
  userID = req.body.userID;
  uniqueName = uuidv4();
  path = 'images/'+uniqueName+'.jpg'
  img.mv(path, function(err){
    if(err)
      return res.status(500).send(err);
    var historyProcess = spawn('python3',["../Utilities/historyRetriever.py",userID]);
    historyProcess.stderr.on('data',function(err){
      console.log(err.toString());
    });
    historyProcess.stdout.on('data',function(data){
      console.log(data.toString());
      history =  JSON.parse(data.toString().replace(/'/g, "\""));
      res.render(__dirname + '/demo.ejs', {
        image_path : path,
        user_id: userID,
        history: history
      });
    });
    var pythonProcess = spawn('python3',["../Team 1/oneShotLearning/Keras2-Oneshot/predictor.py", path]);
    pythonProcess.stdout.on('data', function(data){
      console.log(data.toString());
      io.emit('prediction', data.toString('utf8'));
    });


  });
});
app.post('/food',function(req,res){
  if(!req.body)
    return res.status(400).send('No dish was selected');
  var dish = req.body.dish;
  var pythonProcess = spawn('python3',["../Utilities/mediator.py",rating,userID,dish]);
  pythonProcess.stderr.on('data',function(err){
    console.log(err.toString());
  });
  pythonProcess.stdout.on('data',function(data){
    console.log(data.toString());
    flavorProcess = spawn('python3',["../Team 3/taster.py","--file","../Utilities/input_file.json"]);
    flavorProcess.stderr.on("data",function(err){
      console.log(err.toString());
    });
    flavorProcess.stdout.on("data",function(data){
      console.log(data.toString());
      io.emit('flavors',{flavor:data.toString('utf8'),dishName:dish});
    });

    recommendationProcess = spawn('python3',['../Team 2/Collaborative Filtering/matF.py','--predict',userID]);
    recommendationProcess.stderr.on("data",function(err){
      console.log(err.toString());
    });
    recommendationProcess.stdout.on("data",function(data){
      console.log(data.toString());
      io.emit('recommendations',data.toString('utf8'));
    });
  });
  res.send(200);
});
