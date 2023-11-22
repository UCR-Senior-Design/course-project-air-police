const express = require('express')
const router = express.Router()
const User = require('../models/user')

// Getting all
router.get('/', (req,res) => {
    //res.send('Welcome to the home page!')
    res.render('home', {layout : 'index'});
})


module.exports = router