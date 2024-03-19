const express = require('express')
const router = express.Router()
let { PythonShell } = require("python-shell");

// sql imports
// const mysql = require("mysql2");
const { Pool } = require("pg");
require("dotenv").config();



var img_src = "images/refresh.png";
var monitorId = "default"; // while the python script sees "defualt" it will generate a loading img as a placeholder


function calculateAQI(pm_value, pm_type) {
    let breakpoints, aqi_ranges;
    if (pm_type === 'PM25') {
        breakpoints = [0, 12.1, 35.5, 55.5, 150.5, 250.5, 350.5, 500.5];
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500];
    } else if (pm_type === 'PM10') {
        breakpoints = [0, 54, 154, 254, 354, 424, 504, 604];
        aqi_ranges = [0, 50, 100, 150, 200, 300, 400, 500];
    } else {
        return -1;
    }

    pm_value = parseFloat(pm_value);

    if (isNaN(pm_value)) {
        print("hello")
        return -1;
    }

    for (let i = 0; i < breakpoints.length - 1; i++) {
        if (pm_value >= breakpoints[i] && pm_value <= breakpoints[i + 1]) {
            const aqi = ((aqi_ranges[i + 1] - aqi_ranges[i]) / (breakpoints[i + 1] - breakpoints[i])) * (pm_value - breakpoints[i]) + aqi_ranges[i];
            return Math.round(aqi);
        }
    }
    return -1;
}


var pmValues

async function fetchPMValues(monitorId) {
    const postgreConfig = {
        connectionString: process.env.POSTGRES_URL ,
      };

    try {
        var pool = new Pool(postgreConfig);
        const con = await pool.connect();
        const query = "SELECT pm25, pm10, timestamp FROM Data, Devices WHERE Data.sn = Devices.sn AND Devices.description = ? ORDER BY timestamp DESC LIMIT 1";
        const values = [monitorId];

        // await con.promise().query(query, values)
        // .then(([rows, fields]) => {
        //     // console.log(rows);
        //     result = rows[0];
        //     console.log(result);
        //     return result; 
        // })
        // .catch((err) => {
        //     console.error(err);
        // });
        // const [rows, fields] = await con.promise().query(query, values);
        var result;
        result = await con.query(query, value);
        const rows = result.rows
        await con.release();
        // const result = rows[0];
        return rows;
        
    } catch (error) {
        throw error;
    }
}

async function getAQIValues(monitorId) {
    try {
        const pmValues = await fetchPMValues(monitorId);
        let aqiPM25 = -1;
        let aqiPM10 = -1;
        if(pmValues){
            aqiPM25 = calculateAQI(pmValues.pm25, 'PM25');
            aqiPM10 = calculateAQI(pmValues.pm10, 'PM10');
        }
        // Once the fetchPMValues promise is resolved, calculate AQI
        return { PM25: aqiPM25, PM10: aqiPM10 };
    } catch (error) {
        console.error('Error fetching PM values:', error);
        // Handle error appropriately
    }
    
    // console.log(aqiPM25);
}
const { exec } = require('child_process');
async function makeImgSRC() {
    await new Promise((resolve, reject) => {
    //     let options = {
    //         mode: "text",
    //         pythonPath: ".venv/bin/python",
    //         pythonOptions: ["-u"], // get print results in real-time
    //         args: [monitorId],
    //       };
    //     PythonShell.run("data_call/aqi.py", options).then((result) => {
    //         img_src = "data:image/png;base64,";
    //         img_src = img_src.concat(result)
    //     });
      
        exec(`python data_call/aqi.py`, (error, stdout, stderr)=>{
            if(error){
            console.error('exec error: ${error}');
            return;
            }
            img_src = "data:image/png;base64,";
            img_src = img_src.concat(stdout)
      })
    });
  } 


var aqi = 50; // default value

router.get('/', async (req,res) => {
    monitorId = req.query.monitorId
    await makeImgSRC() // uses python-shell to create the img src from aqi.py

    aqi = await getAQIValues(monitorId); 
    
    if (monitorId) {
        res.render("success-page", { title: 'SUCCESS PAGE ', aqiScore : (aqi.PM25 + aqi.PM10)/2, monitorId, img_src});
        monitorId = req.query.monitorId

        res.status(200);
    }
    else {
        res.redirect('/login');
    }

})


module.exports = router;
