/*
const express = require('express');
const router = express.Router();

router.get('/', (req, res) => {
    //viewData page
    res.render('work-in-progress', {
        title: 'Work in Progress'
    });
});

module.exports = router;
*/
const express = require('express');
const router = express.Router();
const { PythonShell } = require('python-shell');

router.get('/', (req, res) => {
    //executes python script for data analysis
    PythonShell.run('data.py', null, (err, result) => {
        if (err) {
            console.error(err);
            res.status(500).send('Internal Server Error');
        } else {
            //new template to display the data analysis
            res.render('dataAnalysis', {
                title: 'Data Analysis',
                result: result 
            });
            res.status(200); 
        }
    });
});

module.exports = router;
