const express = require('express')
const router = express.Router()
const User = require('../models/user')

// Getting all
router.get('/', (req,res) => {
    res.render('home', {
        title: 'AirPolice'
        //layout: 'home'
    });
})


module.exports = router