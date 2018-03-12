var express = require('express');
var app = express();
var port = process.env.PORT || 3000;
var server = require('http').createServer(app);
var bodyParser = require('body-parser');
var uuidv4 = require('uuid/v4');
var fileUpload = require('express-fileupload');
var spawn = require("child_process").spawn;
var path = require("path");
var io = require('socket.io')(server);
var connections = [];

app.set('view engine', 'ejs');
app.set('views', './views');

app.use(fileUpload());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());
app.use(express.static('css'));
app.use(express.static('js'));
app.use(express.static('images'));
app.use(express.static('resources'));

io.on('connection', function(socket){
    console.log("Client Connected...")
})

app.get('/', function(req, res){
    res.render('index.ejs');
});

app.post('/dashboard', function(req, res){
    var userID = req.body.userID;
    var choice = req.body.options;
    var rating = req.body.rating;
    console.log("UserID: " + userID.toString() + ', Choice: ' + choice + ', Rating:' + rating.toString());

    var history = spawn('python', ["../Utilities/Demo/historyRetriever.py", userID]);
    history.stderr.on('data', function(err){
        console.log(err.toString());
        res.status(500).send(err);
    });
    history.stdout.on('data', function(data){
        var historyData = JSON.parse(data.toString().replace(/'/g,"\""));
        console.log(historyData);
        
        if (choice == 'upload') {
            var img = req.files.uploadDish;
            var uniqueName = uuidv4();
            var fileName = uniqueName+'.jpg'
            var savePath = 'images/'+ fileName;

            res.render('dashboard.ejs', {
                userID: userID,
                rating: rating,
                historyData: historyData,
                choice: choice
            });
    
            img.mv(savePath, function(err){
                if (err){
                    res.status(500).send(err);
                }
                else {
                    var basePath = path.dirname(__dirname);
                    var scriptPath = path.resolve(basePath,'./Team 1/CNTK-2.4/Examples/Image/Detection/FasterRCNN/predictor.py')
                    var imgPath = path.resolve(basePath, 'Demo', savePath);
                    
                    var team1 = spawn('python3.5', [scriptPath, imgPath]);
                    team1.stderr.on('data', function(err){
                        console.log(err.toString());
                    })

                    team1.stdout.on('data', function(data){
                        recognitionData = JSON.parse(data.toString().replace(/'/g,"\""));
                        console.log(recognitionData);
                        io.emit('image', {'path': fileName, 'recognitionData': recognitionData});
                    });
                }
            })
        }
    
        else {
            var dishName = req.body.selectDish;
            var basePath = path.dirname(__dirname);
            var mediatorScript = path.resolve(basePath, './Utilities/Demo/mediator.py');
            var mediator = spawn('python', [mediatorScript, userID, rating, dishName]);
            
            mediator.stderr.on('data', function(err){
                console.log(err.toString());
            });

            mediator.stdout.on('data', function(data){
                console.log(data.toString());
                nutrientData = JSON.parse(data.toString().replace(/'/g,"\""));
                console.log(nutrientData);

                res.render('dashboard.ejs', {
                    userID: userID,
                    dishName: dishName,
                    historyData: historyData,
                    choice: choice,
                    nutrientData: nutrientData
                });
                res.end();

                var team3scriptPath = path.resolve(basePath, './Team 2/taster.py');
                var team3inputFile = path.resolve(basePath, './Utilities/Demo/input_file.json');
                var team3 = spawn('python', [team3scriptPath, '--file', team3inputFile]);

                team3.stderr.on('data', function(err){
                    console.log(err.toString());
                });

                team3.stdout.on('data', function(data){
                    flavourData = JSON.parse(data.toString().replace(/'/g,"\""));
                    console.log(flavourData);

                    io.emit('flavourData', {flavourData: flavourData});

                    var team2scriptPath = path.resolve(basePath, './Team 3/main.py');
                    var team2 = spawn('python', [team2scriptPath, '--factM', '--predict', userID]);

                    team2.stderr.on('data', function(err){
                        console.log(err.toString());
                    });
                    team2.stdout.on('data', function(data){
                        predictionsData = JSON.parse(data.toString());
                        console.log(predictionsData);
                        io.emit('predictions', {'predictions': predictionsData.predicted_rating_list});
                    });
                });
            });
        }    
    })
});

app.post('/workflow', function(req, res){
    var dishName = req.body.dishName;
    var userID = parseInt(req.body.userID);
    var rating = parseInt(req.body.rating);

    var basePath = path.dirname(__dirname);
    var mediatorScript = path.resolve(basePath, './Utilities/Demo/mediator.py');
    console.log(mediatorScript);
    var mediator = spawn('python', [mediatorScript, userID, rating, dishName]);
    
    mediator.stderr.on('data', function(err){
        console.log(err.toString());
    });

    mediator.stdout.on('data', function(data){
        nutrientData = JSON.parse(data.toString().replace(/'/g,"\""));
        console.log(nutrientData);

        var team3scriptPath = path.resolve(basePath, './Team 2/taster.py');
        var team3inputFile = path.resolve(basePath, './Utilities/Demo/input_file.json');
        var team3 = spawn('python', [team3scriptPath, '--file', team3inputFile]);

        team3.stderr.on('data', function(err){
            console.log(err.toString());
        });

        team3.stdout.on('data', function(data){
            flavourData = JSON.parse(data.toString().replace(/'/g,"\""));
            console.log(flavourData);

            io.emit('flavourData', {flavourData: flavourData});

            var team2scriptPath = path.resolve(basePath, './Team 3/main.py');
            var team2 = spawn('python', [team2scriptPath, '--factM', '--predict', userID]);

            team2.stderr.on('data', function(err){
                console.log(err.toString());
            });
            team2.stdout.on('data', function(data){
                predictionsData = JSON.parse(data.toString());
                console.log(predictionsData);
                io.emit('workflow', {'predictions': predictionsData.predicted_rating_list, 'flavourData': flavourData, 'nutrientData':nutrientData});
            });
        });
    });

});

server.listen(port, function(){
    console.log("Server running on port " + port.toString());
})