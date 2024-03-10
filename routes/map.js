const express = require('express')
const router = express.Router()
const { PythonShell } = require("python-shell");


// Getting all
//router.get('/', (req,res) => {
//    res.render('map', {
//        title: 'AirPolice Map'
//        
//    });
//    res.status(200); 
//})


let options = {
    mode: "text",
    pythonPath: ".venv/Scripts/python",
    pythonOptions: ["-u"],
};

PythonShell.run("data_call/generateMap.py", options, (err, results) => {
    if (err) throw err;
    
    const pmTypes = results.map(type => type.trim());
    console.log('Available PM types:', pmTypes);
    
    let mapOptions = {
        mode: "text",
        pythonPath: ".venv/Scripts/python",
        pythonOptions: ["-u"], 
        args: [pmTypes]
    };
    
    PythonShell.run("data_call/generateMap.py", mapOptions, (err, mapResults) => {
        if (err) throw err;
        console.log('Map generation completed');
    });
});
router.post('/changePMType', (req, res) => {
    const selectedPMType = req.body.pmType;

    let options = {
        mode: "text",
        pythonPath: ".venv/Scripts/python",
        pythonOptions: ["-u"], // get print results in real-time
        args: [selectedPMType]
    };

    PythonShell.run("data_call/generateMap.py", options, (err, results) => {
        if (err) throw err;
        console.log('Map generation completed');
    });

    res.redirect('/'); //redirects back to the map page
})


router.get('/', (req,res) => {
    res.render('map', {
        title: 'AirPolice Map'
        
    });
    res.status(200); 
});


module.exports = router