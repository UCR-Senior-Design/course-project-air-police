const express = require('express')
const router = express.Router()
let { PythonShell } = require("python-shell");

// sql imports
const mysql = require("mysql2");
require("dotenv").config();


//////////////////////////
/*
const express = require('express');
const router = express.Router();
const { PythonShell } = require("python-shell");

async function calculateAQI(desc) {
    return new Promise((resolve, reject) => {
        let options = {
            mode: 'text',
            pythonPath: '.venv/Scripts/python',
            pythonOptions: ['-u'],
            args: [desc]
        };

        PythonShell.run('data_call/aqi.py', options, (err, result) => {
            if (err) reject(err);
            resolve(result);
        });
    });
}

async function makeImgSRC(monitorId) {
    return new Promise((resolve, reject) => {
        let options = {
            mode: "text",
            pythonPath: ".venv/Scripts/python",
            pythonOptions: ["-u"], // get print results in real-time
            args: [monitorId],
        };
        PythonShell.run("data_call/aqi.py", options).then((result) => {
            let img_src = "data:image/png;base64,";
            img_src = img_src.concat(result);
            resolve(img_src);
        }).catch(reject);
    });
}

router.get('/', async (req, res) => {
    const monitorId = req.query.monitorId;
   
    try {
        const img_src = await makeImgSRC(monitorId);
        res.render('success-page', { title: 'SUCCESS PAGE', monitorId, img_src });
    } catch (error) {
        console.error('Error calculating AQI:', error);
        res.status(500).send('Error calculating AQI');
    }

});

module.exports = router;
*/


// const express = require('express');
// const router = express.Router();
// const { PythonShell } = require("python-shell");

// const path = require('path');

// let pool;
// PythonShell.run(path.join(__dirname, '..', 'data_call', 'initializeDB.py'), null, function (err, result) {
//     if (err) throw err;
//     console.log('Database connection pool initialized successfully.');
//     pool = result;
// });



var img_src = "images/refresh.png";
var monitorId = "default"; // while the python script sees "defualt" it will generate a loading img as a placeholder


function calculateAQI(pm_value, pm_type) {
    let breakpoints, aqi_ranges;

    if (pm_type === 'PM2.5') {
        breakpoints = [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5];
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500];
    } else if (pm_type === 'PM10') {
        breakpoints = [0, 54, 154, 254, 354, 424, 504, 604];
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500];
    } else {
        return null;
    }

    pm_value = parseFloat(pm_value);

    if (isNaN(pm_value)) {
        return null;
    }

    for (let i = 0; i < breakpoints.length - 1; i++) {
        if (pm_value >= breakpoints[i] && pm_value <= breakpoints[i + 1]) {
            const aqi = ((aqi_ranges[i + 1] - aqi_ranges[i]) / (breakpoints[i + 1] - breakpoints[i])) * (pm_value - breakpoints[i]) + aqi_ranges[i];
            return Math.round(aqi);
        }
    }

    return null;
}


var pmValues

async function fetchPMValues(monitorId) {
    const sqlConfig = {
        connectionLimit: 10,
        host: process.env.mysqlhost,
        port: 3306,
        user: process.env.mysqlUser,
        password: process.env.mysqlPassword,
        database: process.env.mysqlDB,
    };
    var con = mysql.createConnection(sqlConfig);
    try {
        const query = 'SELECT pm25, pm10, timestamp FROM Data WHERE sn IN (SELECT sn FROM Devices WHERE description = ?) ORDER BY timestamp DESC LIMIT 1';
        const values = [monitorId];
        await con.promise().query(query, values)
        .then(([rows, fields]) => {
            pmValues = rows[0];
        })
        .catch((err) => {
            console.error(err);
        });
        //return result[0]; 
    } catch (error) {
        throw error;
    }
}

async function getAQIValues(monitorId) {
    try {
        await fetchPMValues(monitorId);
        const aqiPM25 = calculateAQI(pmValues.pm25, 'PM25');
        const aqiPM10 = calculateAQI(pmValues.pm10, 'PM10');
        return { PM25: aqiPM25, PM10: aqiPM10 };
    } catch (error) {
        throw error;
    }
}

async function makeImgSRC() {
    await new Promise((resolve, reject) => {
        let options = {
            mode: "text",
            pythonPath: ".venv/bin/python",
            pythonOptions: ["-u"], // get print results in real-time
            args: [monitorId],
          };
        PythonShell.run("data_call/aqi.py", options).then((result) => {
            //   if (err) {
            //       console.error('Error fetching AQI data:', err);
            //       return;
            //   }
            img_src = "data:image/png;base64,";
            img_src = img_src.concat(result)
        });
      });
  } 

// router.get('/', async (req, res) => {
//     const monitorId = req.query.monitorId;

//     try {
//         const aqi = await getAQIValues(monitorId);
//         const img_src = await makeImgSRC(monitorId);
//         res.render('success-page', { title: 'SUCCESS PAGE', monitorId, aqi, img_src });
//     } catch (error) {
//         console.error('Error fetching AQI values:', error);
//         res.status(500).send('Error fetching AQI values');
//     }
// });

var aqi = 50; // default value

router.get('/', (req,res) => {
    monitorId = req.query.monitorId
    makeImgSRC() // uses python-shell to create the img src from aqi.py

    // aqi = getAQIValues(monitorId); // this just returns a pending promise so I'm commenting it out for now
    
    if (req.session.logged_in) {
        res.render("success-page", { title: 'SUCCESS PAGE ', aqi, monitorId, img_src});
        monitorId = req.query.monitorId

        res.status(200);
    }
    else {
        res.redirect('/login');
    }

})


module.exports = router;
