const express = require("express");
const router = express.Router();
const jwt = require("jsonwebtoken");
const mysql = require("mysql2");
// Getting all
router.get("/", async (req, res) => {
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB,
  });
  var query = "SELECT * FROM User WHERE username = ?";

  const token = req.session.token;
  let user;
  let isPorter = false;
  if (token) {
    jwt.verify(token, process.env.key, (error, decoded) => {
      if (error) {
        isPorter = false;
        //  add errors here redirecting
        // res.redirect('/home');
      }
      user = decoded.username;
    });
  }
  if (user === process.env.porterUser) {
    isPorter = true;
  } else {
    isPorter = false;
  }
  let value = [user];
  var result;
  await con
    .promise()
    .query(query, value)
    .then(([rows, fields]) => {
      result = rows;
    })
    .catch((err) => {
      console.error(err);
    });
  if (result.length != 0) {
    res.render("table", {
      title: "AirPolice Map",
      body: "success",
      isLoggedIn: true,
      isPorterUser: isPorter,
    });
    res.status(200);
  } else {
    res.redirect("/rlogin?error=ngl");
  }
});

module.exports = router;
