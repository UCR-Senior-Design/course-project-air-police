const express = require("express");
const router = express.Router();
const { exec } = require('child_process');
// Getting all
router.get("/", async (req, res) => {
try{
  const response  = await fetch('/api/api/genMap', {
    method:"POST",
    headers:{
      'Content-Type': 'application/json',
      'pm_type': 'pm25'
    }
  })
  const response2  = await fetch('/api/api/genMap', {
    method:"POST",
    headers:{
      'Content-Type': 'application/json',
      'pm_type': 'pm10'
    }
  })
}
catch(error){
  console.error("error executing map: " + error)
}
  res.render("home", {
    title: "AirPolice",
  });
  res.status(200);
});

module.exports = router;
