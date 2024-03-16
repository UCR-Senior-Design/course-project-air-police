const express = require('express')
const router = express.Router()

var img_src = "images/refresh.png";
var monitorId = "SSIF_A3_704"; // replace with "default" to make flexible

let { PythonShell } = require("python-shell");

let options = {
    mode: "text",
    pythonPath: ".venv/bin/python",
    pythonOptions: ["-u"], // get print results in real-time
    args: [monitorId],
  };
  async function makeImgSRC() {
    await new Promise((resolve, reject) => {
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

