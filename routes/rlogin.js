const express = require("express");
const router = express.Router();
const { Pool } = require("pg");
const jwt = require("jsonwebtoken");
const { exec } = require('child_process');
const postgreConfig = {
  connectionString: process.env.POSTGRES_URL ,
};
router.get("/", async (req, res) => {


  try{
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    const cookieHeader = req.headers.cookie;
    if(!cookieHeader){
      res.render("rlogin", {
        title: "LOGIN ",
        displayText: "researcher login test",
      });
      res.status(200);
    }
    const cookies = cookieHeader.split(';');
    const tokenCookie = cookies.find(cookie => cookie.trim().startsWith('token='));

    if (tokenCookie) {
        const token = tokenCookie.split('=')[1];
        // Token exists, continue processing
    } 
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
    await con.release();
    if (rows.length > 0) {
      res.redirect("/table");
    } else {
      res.render("rlogin", {
        title: "LOGIN ",
        displayText: "researcher login ",
      });
      res.status(200);
    }
  }catch(error){
    console.error(error);
  }

});
module.exports = router;
