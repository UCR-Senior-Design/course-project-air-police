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

