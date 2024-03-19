const express = require("express");
const router = express.Router();
const { exec } = require('child_process');
// Getting all
router.get("/", (req, res) => {
  res.render("home", {
    title: "AirPolice",
  });
  res.status(200);
});


const param = "pm25";
exec('python data_call/generateMap.py ${param}', (error, stdout, stderr)=>{
  if(error){
    console.error('exec error: ${error}');
    return;
  }
})
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
