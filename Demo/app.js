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
var fs = require('fs');

app.set('view engine', 'ejs');
app.set('views', './views');

app.use(fileUpload());
app.use(bodyParser.urlencoded({ extended: false, limit: '50mb', extended: true }));
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

app.post('/workflow', function(req, res){
    var choice = req.body.choiceRadio;
    if (choice == 'search'){
        console.log(req.body.dishNames);
        console.log(req.body.ratings);
        var mediator = spawn('python', ['../Utilities/Demo/mediator.py', req.body.userID, req.body.ratings, req.body.dishNames]);
        mediator.stderr.on('data', function(err){
            console.log(err.toString());
            res.status(500).send();
        });

        mediator.stdout.on('data', function(data){
            var data = JSON.parse(data.toString().replace(/'/g,"\""));
            console.log(data);
            res.json(data);
        });
    }    
    else{
        var img = req.files.uploadDish;
        var uniqueName = uuidv4();
        var fileName = uniqueName+'.jpg'
        var savePath = 'images/'+ fileName;
        img.mv(savePath, function(err){
            if (err){
                res.status(500).send(err);
            }
            else {
                console.log("Done moving to " + savePath);
                var basePath = path.dirname(__dirname);
                var scriptPath = path.resolve(basePath,'./Utilities/Demo/dummyTeam1.py');
                // var imgPath = path.resolve(basePath, 'Demo', savePath);
                
                // var team1 = spawn('python3.5', [scriptPath, imgPath]);
                var team1 = spawn('python3.5', [scriptPath]);
                team1.stderr.on('data', function(err){
                    console.log(err.toString());
                })

                team1.stdout.on('data', function(data){
                    recognitionData = JSON.parse(data.toString().replace(/'/g,"\""))['predictions'][0];
                    print(recognitionData);
                });
            }
        })
    }
});

app.post('/getrecommendations', function(req, res){
    var steps = 7000;
    var floors = 2;
    var matf = spawn('python', ['../Team 3/main.py', '--matF', '--predict', req.body.userID, '--health', '--steps', steps, '--floors', floors]);
    var tfidf = spawn('python', ['../Team 3/main.py', '--tfidf', '--predict', req.body.userID, '--health', '--steps', steps, '--floors', floors]);
    var tfidfflavour = spawn('python', ['../Team 3/main.py', '--tfidf', '--flavour', '--predict', req.body.userID, '--health', '--steps', steps, '--floors', floors]);
    var doneflag = 0;
    var notdoneflag = 0;
    var retval = {};

    console.log(req.body.userID);
    matf.stderr.on('data', function(err){
        console.log(err.toString());
        notdoneflag += 1;
    });
    tfidf.stderr.on('data', function(err){
        console.log(err.toString());
        notdoneflag += 1;
    });
    tfidfflavour.stderr.on('data', function(err){
        console.log(err.toString());
        notdoneflag += 1;
    });

    matf.stdout.on('data', function(data){
        var data = JSON.parse(data.toString().replace(/'/g,"\""));
        retval['matf'] = data.predicted_rating;
        doneflag += 1;
    });
    tfidf.stdout.on('data', function(data){
        var data = JSON.parse(data.toString().replace(/'/g,"\""));
        retval['tfidf'] = data.predicted_rating;
        doneflag += 1;
    });
    tfidfflavour.stdout.on('data', function(data){
        var data = JSON.parse(data.toString().replace(/'/g,"\""));
        retval['tfidfflavour'] = data.predicted_rating;
        doneflag += 1;
    });

    interval = setInterval(function(){
        if (doneflag > 2) {
            clearInterval(interval);
            res.json(retval);
        }
    }, 100);
});

app.post('/retrain', function(req, res){
    var steps = 7000;
    var floors = 2;
    var matf = spawn('python', ['../Team 3/main.py', '--matF', '--predict', req.body.userID, '--retrain', '--health', '--steps', steps, '--floors', floors]);
    var tfidf = spawn('python', ['../Team 3/main.py', '--tfidf', '--predict', req.body.userID, '--health', '--steps', steps, '--floors', floors]);
    var tfidfflavour = spawn('python', ['../Team 3/main.py', '--tfidf', '--flavour', '--predict', req.body.userID, '--health', '--steps', steps, '--floors', floors]);
    var doneflag = 0;
    var notdoneflag = 0;
    var retval = {};

    console.log(req.body.userID);
    matf.stderr.on('data', function(err){
        console.log(err.toString());
        notdoneflag += 1;
    });
    tfidf.stderr.on('data', function(err){
        console.log(err.toString());
        notdoneflag += 1;
    });
    tfidfflavour.stderr.on('data', function(err){
        console.log(err.toString());
        notdoneflag += 1;
    });

    matf.stdout.on('data', function(data){
        var data = JSON.parse(data.toString().replace(/'/g,"\""));
        retval['matf'] = data.predicted_rating;
        doneflag += 1;
    });
    tfidf.stdout.on('data', function(data){
        var data = JSON.parse(data.toString().replace(/'/g,"\""));
        retval['tfidf'] = data.predicted_rating;
        doneflag += 1;
    });
    tfidfflavour.stdout.on('data', function(data){
        var data = JSON.parse(data.toString().replace(/'/g,"\""));
        retval['tfidfflavour'] = data.predicted_rating;
        doneflag += 1;
    });

    interval = setInterval(function(){
        if (doneflag > 2) {
            clearInterval(interval);
            res.json(retval);
        }
    }, 100);
});

app.post('/dashboard', function(req, res){
    var userID = req.body.userID;
    console.log("UserID: " + userID.toString());

    // Retrive User history and User Data
    var userData = spawn('python', ['../Utilities/Demo/historyRetriever.py', userID]);
    userData.stderr.on('data', function(err){
        console.log(err.toString());
        res.status(500).send(err);
    });

    userData.stdout.on('data', function(data){
        var data = JSON.parse(data.toString().replace(/'/g,"\""));
        console.log(data);

        res.render('dashboard.ejs', {
            userID: userID,
            historyData: data['history'],
            userData: data['userData']
        });
    });

    // var history = spawn('python', ["../Utilities/Demo/historyRetriever.py", userID]);
    // history.stderr.on('data', function(err){
    //     console.log(err.toString());
    //     res.status(500).send(err);
    // });
    // history.stdout.on('data', function(data){
    //     var historyData = JSON.parse(data.toString().replace(/'/g,"\""));
    //     console.log(historyData);
        
    //     if (choice == 'upload') {
    //         var img = req.files.uploadDish;
    //         var uniqueName = uuidv4();
    //         var fileName = uniqueName+'.jpg'
    //         var savePath = 'images/'+ fileName;

    //         res.render('dashboard.ejs', {
    //             userID: userID,
    //             rating: rating,
    //             historyData: historyData,
    //             choice: choice
    //         });
    
    //         img.mv(savePath, function(err){
    //             if (err){
    //                 res.status(500).send(err);
    //             }
    //             else {
    //                 var basePath = path.dirname(__dirname);
    //                 var scriptPath = path.resolve(basePath,'./Team 1/CNTK-2.4/Examples/Image/Detection/FasterRCNN/predictor.py')
    //                 var imgPath = path.resolve(basePath, 'Demo', savePath);
                    
    //                 var team1 = spawn('python3.5', [scriptPath, imgPath]);
    //            +
    //`   `     team1.stderr.on('data', function(err){
    //                     console.log(err.toString());
    //                 })

    //                 team1.stdout.on('data', function(data){
    //                     recognitionData = JSON.parse(data.toString().replace(/'/g,"\""));
    //                     console.log(recognitionData);
    //                     io.emit('image', {'path': fileName, 'recognitionData': recognitionData});
    //                 });
    //             }
    //         })
    //     }
    
    //     else {
    //         var dishName = req.body.selectDish;
    //         var basePath = path.dirname(__dirname);
    //         var mediatorScript = path.resolve(basePath, './Utilities/Demo/mediator.py');
    //         var mediator = spawn('python', [mediatorScript, userID, rating, dishName]);
            
    //         mediator.stderr.on('data', function(err){
    //             console.log(err.toString());
    //         });

    //         mediator.stdout.on('data', function(data){
    //             console.log(data.toString());
    //             nutrientData = JSON.parse(data.toString().replace(/'/g,"\""));
    //             console.log(nutrientData);

    //             res.render('dashboard.ejs', {
    //                 userID: userID,
    //                 dishName: dishName,
    //                 historyData: historyData,
    //                 choice: choice,
    //                 nutrientData: nutrientData
    //             });
    //             res.end();

    //             var team3scriptPath = path.resolve(basePath, './Team 2/taster.py');
    //             var team3inputFile = path.resolve(basePath, './Utilities/Demo/input_file.json');
    //             var team3 = spawn('python', [team3scriptPath, '--file', team3inputFile]);

    //             team3.stderr.on('data', function(err){
    //                 console.log(err.toString());
    //             });

    //             team3.stdout.on('data', function(data){
    //                 flavourData = JSON.parse(data.toString().replace(/'/g,"\""));
    //                 console.log(flavourData);

    //                 io.emit('flavourData', {flavourData: flavourData});

    //                 var team2scriptPath = path.resolve(basePath, './Team 3/main.py');
    //                 var team2 = spawn('python', [team2scriptPath, '--factM', '--predict', userID]);

    //                 team2.stderr.on('data', function(err){
    //                     console.log(err.toString());
    //                 });
    //                 team2.stdout.on('data', function(data){
    //                     predictionsData = JSON.parse(data.toString());
    //                     console.log(predictionsData);
    //                     io.emit('predictions', {'predictions': predictionsData.predicted_rating_list});
    //                 });
    //             });
    //         });
    //     }    
    // })
});

/*app.post('/workflow', function(req, res){


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

});*/

server.listen(port, function(){
    console.log("Server running on port " + port.toString());
})