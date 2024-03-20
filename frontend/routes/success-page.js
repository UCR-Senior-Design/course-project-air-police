const express = require('express')
const router = express.Router()

// sql imports
// const mysql = require("mysql2");
const { Pool } = require("pg");
require("dotenv").config();
const pythonPath = require.resolve('python');


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
    // console.log(pm_value)
    pm_value = parseFloat(pm_value);
    
    if (isNaN(pm_value)) {
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
const postgreConfig = {
    connectionString: process.env.POSTGRES_URL ,
  };
async function fetchPMValues(monitorId) {
    

    try {
        var pool = new Pool(postgreConfig);
        const con = await pool.connect();
        const query = "SELECT pm25, pm10, timestamp FROM Data, Devices WHERE Data.sn = Devices.sn AND Devices.description = $1 ORDER BY timestamp DESC LIMIT 1";
        const value = [monitorId];
        let result;
        result = await con.query(query, value);
        const rows = result.rows[0];
        console.log(rows);
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
            console.log('hi');
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
const fs = require('fs');
const path = require('path');

async function makeImgSRC() {
    try{
        const response = await fetch('/api/aqi.py', {
            method:'POST',
            headers: {
                "description": monitorId
            }
        });
        const data = await response.json();
        img_src = "data:image/png;base64,";
        img_src = img_src.concat(data.b64);
    }
    catch(error){
        console.error("Error Fetching Data: ", error);
        throw error;
    }
  } 


var aqi = 50; // default value

router.get('/', async (req,res) => {
    monitorId = req.query.monitorId
    // uses python-shell to create the img src from aqi.py
    try{
    await makeImgSRC() 
    console.log(img_src)
    aqi = await getAQIValues(monitorId); 
    
    if (monitorId) {
        res.render("success-page", { title: 'SUCCESS PAGE ', aqiScore : (aqi.PM25 + aqi.PM10)/2, monitorId, img_src});
        res.status(200);
    }
    else {
        res.redirect('/login');
    }
}catch(error){
    console.error(error);
}

})


module.exports = router;
