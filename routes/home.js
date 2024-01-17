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

// Runs test.py once the website starts running
let {PythonShell} = require('python-shell')

let options = {
    mode: 'text',
    pythonPath: '.venv/bin/python3',
    pythonOptions: ['-u'], // get print results in real-time
  };
  
  PythonShell.run('data_call/data.py', options).then(messages=>{
    console.log('executed data.py');
  });


module.exports = router