const express = require("express");
const router = express.Router();
const { Pool } = require("pg");
const jwt = require("jsonwebtoken");

const postgreConfig = {
  connectionString: process.env.POSTGRES_URL ,
};
router.get("/", async (req, res) => {
  // if(req.session.logged_in){
  //   res.redirect('/table') // sends status code 302 by default
  // }else{
  try{
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
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
    await con.release();
    if (rows.length > 0) {
      res.redirect("/table");
    } else {
      res.render("rlogin", {
        title: "LOGIN ",
        displayText: "researcher login test",
      });
      res.status(200);
    }
  }catch(error){
    console.error(error);
  }

});
module.exports = router;
