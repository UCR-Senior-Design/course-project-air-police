/*
const express = require('express')
const router = express.Router()

//const { calculateAQI } = require('./');

router.get('/', (req, res) => {
    const monitorId = req.query.monitorId;

    const pm25 = getPM25Value(monitorId); 
    const pm10 = getPM10Value(monitorId); 
    const aqi = calculateAQI(pm25, pm10);

    

    //For now, let's just render a page that displays the success
    res.render("success-page", { title: 'SUCCESS PAGE ', displayText: 'participant login test' });
    res.status(200);
})

module.exports = router;

*/
const express = require('express')
const router = express.Router()


router.get('/', (req,res) => {
    
    res.render("success-page", { title: 'SUCCESS PAGE ', monitorId : req.query.monitorId });
    res.status(200);
})

//const { fetchData } = require('./data_call/data.py');

router.get('/aqiData', (req, res) => {
    const monitorId = req.query.monitorId;
    const data = fetchData(monitorId);
    res.json(data);
});


//const { fetchData } = require('./data');

router.get('/aqiData', (req, res) => {
    const data = fetchData();
    res.json(data);
});


module.exports = router;


