/*
const express = require('express')
const router = express.Router()

var img_src = "images/refresh.png";
var monitorId = "default"; // while the python script sees "defualt" it will generate a loading img as a placeholder

let { PythonShell } = require("python-shell");

router.get('/', async (req, res) => {
    const monitorId = req.query.monitorId;
    
    //calculate AQI
    async function calculateAQI(desc) {
        return new Promise((resolve, reject) => {
            let options = {
                mode: 'text',
                pythonPath: '.venv/Scripts/python',
                pythonOptions: ['-u'],
                args: [desc]
            };

            PythonShell.run('data_call/aqi.py', options, (err, result) => {
                if (err) reject(err);
                resolve(result);
            });
        });
    }

    if (req.session.logged_in) {
        try {
            const img_src = await calculateAQI(monitorId);
            res.render('success-page', { title: 'SUCCESS PAGE', monitorId, img_src });
        } catch (error) {
            console.error('Error calculating AQI:', error);
            res.status(500).send('Error calculating AQI');
        }
    } else {
        res.redirect('/login');
    }
});



  async function makeImgSRC() {
    await new Promise((resolve, reject) => {
        let options = {
            mode: "text",
            pythonPath: ".venv/Scripts/python",
            pythonOptions: ["-u"], // get print results in real-time
            args: [monitorId],
          };
        PythonShell.run("data_call/aqi.py", options).then((result) => {
            //   if (err) {
            //       console.error('Error fetching AQI data:', err);
            //       return;
            //   }
            img_src = "data:image/png;base64,";
            img_src = img_src.concat(result)
        });
      });
  } 

router.get('/', (req,res) => {
    monitorId = req.query.monitorId
    makeImgSRC() // uses python-shell to create the img src from aqi.py
    
    
    if (req.session.logged_in) {
        res.render("success-page", { title: 'SUCCESS PAGE ', monitorId, img_src});
        monitorId = req.query.monitorId
        res.status(200);

    }
    else {
        res.redirect('/login');
    }

})

module.exports = router;
*/
const express = require('express');
const router = express.Router();
const { PythonShell } = require("python-shell");

async function calculateAQI(desc) {
    return new Promise((resolve, reject) => {
        let options = {
            mode: 'text',
            pythonPath: '.venv/Scripts/python',
            pythonOptions: ['-u'],
            args: [desc]
        };

        PythonShell.run('data_call/aqi.py', options, (err, result) => {
            if (err) reject(err);
            resolve(result);
        });
    });
}

async function makeImgSRC(monitorId) {
    return new Promise((resolve, reject) => {
        let options = {
            mode: "text",
            pythonPath: ".venv/Scripts/python",
            pythonOptions: ["-u"], // get print results in real-time
            args: [monitorId],
        };
        PythonShell.run("data_call/aqi.py", options).then((result) => {
            let img_src = "data:image/png;base64,";
            img_src = img_src.concat(result);
            resolve(img_src);
        }).catch(reject);
    });
}

router.get('/', async (req, res) => {
    const monitorId = req.query.monitorId;
    /* //attempting to make this work
    try {
        const [img_src, aqi] = await Promise.all([
            makeImgSRC(monitorId),
            calculateAQI(monitorId)
        ]);

        const aqiValues = JSON.parse(aqi);

        res.render('success-page', { title: 'SUCCESS PAGE', monitorId, img_src, aqi: aqiValues });
    } catch (error) {
        console.error('Error calculating AQI:', error);
        res.status(500).send('Error calculating AQI');
    }
    */
    try {
        const img_src = await makeImgSRC(monitorId);
        res.render('success-page', { title: 'SUCCESS PAGE', monitorId, img_src });
    } catch (error) {
        console.error('Error calculating AQI:', error);
        res.status(500).send('Error calculating AQI');
    }

});

module.exports = router;
