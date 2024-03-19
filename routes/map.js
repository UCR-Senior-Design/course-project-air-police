const express = require("express");
const router = express.Router();
const { Pool } = require("pg");
const jwt = require("jsonwebtoken");
// let { PythonShell } = require("python-shell");

const { exec } = require('child_process');
// Getting all
//router.get('/', (req,res) => {
//    res.render('map', {
//        title: 'AirPolice Map'
//
//    });
//    res.status(200);
//})
const postgreConfig = {
  connectionString: process.env.POSTGRES_URL ,
};

router.get("/", async (req, res) => {
  var map
  const param = "pm25";
  exec(`python data_call/generateMap.py ${param}`, (error, stdout, stderr)=>{
  if(error){
    console.error('exec error: ${error}');
  }
  map = stdout
  })

  try {
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    const cookieHeader = req.headers.cookie;
    if(!cookieHeader){
      res.redirect('/rlogin');
      return;
    }
    const cookies = cookieHeader.split(';');
    const token = cookies.find(cookie => cookie.trim().startsWith('token=')).split('=')[1];
    let user;
    let isPorter = false;
    if (token) {
      jwt.verify(token, process.env.key, (error, decoded) => {
        if (error) {
          isPorter = false;
        }
        user = decoded.username;
      });
    }
    if (user === process.env.porterUser) {
      isPorter = true;
    } else {
      isPorter = false;
    }
    var query = "SELECT username FROM usrs WHERE username = $1";
    let value = [user];
    var result;
    result = await con.query(query, value);
    const rows = result.rows;
    await con.release();
    if (rows.length > 0) {
      // res.render("map", {
      //   title: "AirPolice Map",
      // });
      // res.status(200);
      // res.status(200).send(map);
    } else {
      res.redirect("/rlogin?error=ngl");
    }
  } catch (error) {
    console.error(error);
  }
});

module.exports = router;
