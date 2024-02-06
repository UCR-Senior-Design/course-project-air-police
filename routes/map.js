const express = require('express')
const router = express.Router()

// Getting all
router.get('/', (req,res) => {
    res.render('map', {
        title: 'AirPolice Map'
        
    });
    res.sendStatus(200); 
})


module.exports = router