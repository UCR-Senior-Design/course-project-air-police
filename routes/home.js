const express = require('express')
const router = express.Router()
const User = require('../models/user')

// Getting all
router.get('/', (req,res) => {
    res.send('Hello World')
})

router.get('/:id', (req, res) => {

})

router.post('/', (req, res) => {

})

module.exports = router