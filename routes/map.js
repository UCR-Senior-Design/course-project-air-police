const express = require('express')
const router = express.Router()

// Getting all
router.get('/', (req,res) => {
    res.render('map', {
        title: 'AirPolice Map'
        
    });
})


module.exports = router