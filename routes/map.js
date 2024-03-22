const express = require("express");
const router = express.Router();
const { Pool } = require("pg");
const jwt = require("jsonwebtoken");
// let { PythonShell } = require("python-shell");

const { exec } = require('child_process');
const { createClient } = require('contentful');
// Getting all
//router.get('/', (req,res) => {
//    res.render('map', {
//        title: 'AirPolice Map'
//
//    });
//    res.status(200);
//})
const {getID, changeMap} = require('./changepm.js')
const postgreConfig = {
  connectionString: process.env.POSTGRES_URL ,
};
const genData = require("../helperFunctions/genMap.js");

router.get("/", async (req, res) => {
  try {
    const {data, central_lat, central_lon} = await genData(getID);
    var datas = JSON.stringify(data);
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    const cookieHeader = req.headers.cookie;
    if(!cookieHeader){
      res.redirect('/rlogin');
      return;
    }
    const cookies = cookieHeader.split(';');
    const tokenCookie = cookies.find(cookie => cookie.trim().startsWith('token='));
    var token;
    if (tokenCookie) {
        token = tokenCookie.split('=')[1];
        // Token exists, continue processing
    } else {
        res.redirect('/rlogin?error=ngl');
    }
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
      var pm_type = {
        pm_type:getID()};
      pm_type = JSON.stringify(pm_type);
      res.render('map', {
        datas: datas,
        central_lat: central_lat,
        central_lon: central_lon,
        pm_type: pm_type
      });
      // res.status(200).send(map);
    } else {
      res.redirect("/rlogin?error=ngl");
    }
  } catch (error) {
    console.error(error);
  }
});

module.exports = router;

