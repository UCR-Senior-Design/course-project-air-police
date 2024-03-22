const express = require("express");
const router = express.Router();
const jwt = require("jsonwebtoken");
const { Pool } = require("pg");
// Getting all
const postgreConfig = {
  connectionString: process.env.POSTGRES_URL ,
};
// var tableData;
// var errorTable;
// async function fetchTableData() {
//   // pull researcher table data from sql db, export it as json response
//   try {
//     var pool = new Pool(postgreConfig);
//     const con = await pool.connect();
//     var query1 =
//       "SELECT Devices.sn, Devices.pmhealth, Devices.sdhealth,Devices.onlne, CONCAT(ROUND(Devices.datafraction*100,2),'%') AS datafraction, Data.pm25, Data.pm10,  SUBSTRING(Data.timestamp,1,10) AS timestamp FROM Devices LEFT JOIN ( SELECT d1.* FROM Data d1 JOIN ( SELECT sn, MAX(timestamp) AS max_timestamp FROM Data GROUP BY sn ) d2 ON d1.sn = d2.sn AND d1.timestamp = d2.max_timestamp ) AS Data ON Data.sn = Devices.sn ORDER BY Devices.sn;";
//     var result = await con.query(query1);
//     // if (result) {
//       tableData = result.rows;
//     // }
//     var query2 =
//       "SELECT Devices.sn, Devices.description, Devices.pmhealth, Devices.sdhealth, Devices.onlne, CONCAT(ROUND(Devices.datafraction*100,2),'%') AS datafraction , SUBSTRING(Devices.last_seen,1,10) AS last_seen FROM Devices WHERE Devices.sdHealth = 'ERROR' OR Devices.pmHealth='ERROR' OR Devices.onlne = 'offline' ORDER BY Devices.onlne, Devices.sdHealth DESC, Devices.pmHealth DESC;";
//     result = await con.query(query2);
//     errorTable = result.rows;
//     await con.release();
//   } catch (error) {
//     console.error(error);
//   }
// }
router.get("/", async (req, res) => {
  try {
    // await fetchTableData()
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    var query = "SELECT * FROM usrs WHERE username = $1";
    const cookieHeader = req.headers.cookie;
    if(!cookieHeader){
      res.redirect('/rlogin?error=ngl');
      return;
    }
    const cookies = cookieHeader.split(';');
    const tokenCookie = cookies.find(cookie => cookie.trim().startsWith('token='));

    if (tokenCookie) {
        const token = tokenCookie.split('=')[1];
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
      await con.release();
      res.render("table", {
        title: "AirPolice Map",
        body: "success",
        isLoggedIn: true,
        isPorterUser: isPorter,
      });
      res.status(200);
    } else {
      await con.release();
      res.redirect("/rlogin?error=ngl");
    }
  } catch (error) {
    console.error(error);
  }
});

module.exports = router;
