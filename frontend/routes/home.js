const express = require("express");
const router = express.Router();
const { exec } = require('child_process');
// Getting all
router.get("/", async (req, res) => {

  const response  = await fetch('/api/genMap', {
    method:"POST",
    headers:{
      pm_type: 'pm25'
    }
  })
  const response2  = await fetch('/api/genMap', {
    method:"POST",
    headers:{
      pm_type: 'pm10'
    }
  })
  res.render("home", {
    title: "AirPolice",
  });
  res.status(200);
});



// Runs test.py once the website starts running
// let { PythonShell } = require("python-shell");

// let options = {
//   mode: "text",
//   pythonPath: ".venv/bin/python",
//   pythonOptions: ["-u"], // get print results in real-time
//   args: ["pm25"],
// };

// PythonShell.run("data_call/generateMap.py", options);

module.exports = router;
