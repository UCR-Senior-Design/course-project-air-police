const express = require("express");
const router = express.Router();
const jwt = require("jsonwebtoken");
const { Pool } = require("pg");
// Getting all
const postgreConfig = {
  connectionString: process.env.POSTGRES_URL ,
};
router.get("/", async (req, res) => {
  try {
    var con = new Pool(postgreConfig);
    await con.connect();
    var query = "SELECT * FROM usrs WHERE username = $1";
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

    var query = "SELECT username FROM usrs WHERE username = $1";
    let value = [user];
    var result;
    result = await con.query(query, value);
    const rows = result.rows;

    if (rows.length > 0) {
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
  } catch (error) {
    console.error(error);
  }
});

module.exports = router;
