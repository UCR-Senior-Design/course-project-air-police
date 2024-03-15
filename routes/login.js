const express = require("express");
const router = express.Router();
const { Client } = require("pg");
require("dotenv").config();

// get list of monitor login keys then place them in monitorKeys
var monitorKeys;

async function fetchMonitorDesc() {
  const postgreConfig = {
    user: process.env.postgreUser,
    host: process.env.postgreHost,
    database: process.env.postgreDB,
    password: process.env.postgrePassword,
    port: process.env.postgrePort,
  };
  var con = new Client(postgreConfig);
  await con.connect();
  var query1 = "SELECT description FROM Devices;";

  // await con.promise().query(query1)
  // .then(([rows, fields]) => {
  //     monitorKeys = rows;
  // })
  // .catch((err) => {
  //     console.error(err);
  // });
  var results = await con.query(query1);
  await con.end();
  monitorKeys = results.rows;
}
fetchMonitorDesc(); // update monitorKeys list

function checkValid(monitorId) {
  // Check if entered monitor ID is in the list
  for (var i in monitorKeys) {
    if (monitorId === monitorKeys[i].description) {
      return true;
    }
  }
  return false;
}

router.get("/", (req, res) => {
  const monitorId = req.query.monitorId;
  var valid = false;

  if (monitorId != null) {
    console.log("Submitted monitor ID:", monitorId);
    valid = checkValid(monitorId);
  }
  if (valid) {
    req.session.logged_in = true;
    res.redirect("/success-page?monitorId=" + monitorId); // sends status code 302 by default
  } else {
    res.render("login", {
      title: "Participant Login",
      monitorId: req.query.monitorId,
    });
    res.status(200);
  }
});

module.exports = router;
