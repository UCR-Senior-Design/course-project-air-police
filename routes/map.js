const express = require("express");
const router = express.Router();
let { PythonShell } = require("python-shell");

// Getting all
//router.get('/', (req,res) => {
//    res.render('map', {
//        title: 'AirPolice Map'
//
//    });
//    res.status(200);
//})

router.get("/", (req, res) => {
  res.render("map", {
    title: "AirPolice Map",
  });
  res.status(200);
});

module.exports = router;
