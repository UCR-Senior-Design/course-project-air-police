const express = require("express");
const router = express.Router();

// Getting all
router.get("/", (req, res) => {
  res.render("home", {
    title: "AirPolice",
  });
  res.status(200);
});

// Runs test.py once the website starts running
let { PythonShell } = require("python-shell");

let options = {
  mode: "text",
  pythonPath: ".venv/bin/python",
  pythonOptions: ["-u"], // get print results in real-time
};

PythonShell.run("data_call/generateMap.py", options);

module.exports = router;
