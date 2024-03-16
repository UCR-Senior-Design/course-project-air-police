const express = require('express')
const router = express.Router()

var img_src = "images/refresh.png";
var monitorId = "default"; // while the python script sees "defualt" it will generate a loading img as a placeholder

let { PythonShell } = require("python-shell");


  async function makeImgSRC() {
    await new Promise((resolve, reject) => {
        let options = {
            mode: "text",
            pythonPath: ".venv/bin/python",
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

