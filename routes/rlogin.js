const express = require("express");
const router = express.Router();
const { Client } = require("pg");
const jwt = require("jsonwebtoken");

const postgreConfig = {
  user: process.env.postgreUser,
  host: process.env.postgreHost,
  database: process.env.postgreDB,
  password: process.env.postgrePassword,
  port: process.env.postgrePort,
};
router.get("/", async (req, res) => {
  // if(req.session.logged_in){
  //   res.redirect('/table') // sends status code 302 by default
  // }else{
  var con = new Client(postgreConfig);
  await con.connect();
  const token = req.session.token;
  let user;
  if (token) {
    jwt.verify(token, process.env.key, (error, decoded) => {
      if (error) {
        console.error(error);
      }
      user = decoded.username;
    });
  }
  var query = "SELECT username FROM usrs WHERE username = $1";
  let value = [user];
  var result;
  result = await con.query(query, value);
  const rows = result.rows;
  if (rows.length > 0) {
    res.redirect("/table");
  } else {
    res.render("rlogin", {
      title: "LOGIN ",
      displayText: "researcher login test",
    });
    res.status(200);
  }
});
module.exports = router;
