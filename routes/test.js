const express = require('express')
const router = express.Router()

// Getting all
router.get('/', (req,res) => {
    res.render('test', {
        title: 'AirPolice Map',
        body: 'success'
    });
})


module.exports = router