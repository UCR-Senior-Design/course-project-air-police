// --------------- code for connecting to the database ---------------

require("dotenv").config();
const bodyParser = require("body-parser");
var bcrypt = require("bcryptjs");
var jwt = require("jsonwebtoken");
const nodemailer = require("nodemailer");
const hash = process.env.hash;
const mysql = require("mysql2");
// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const { request } = require("http");

const sqlConfig = {
  connectionLimit: 10,
  host: process.env.mysqlhost,
  port: 3306,
  user: process.env.mysqlUser,
  password: process.env.mysqlPassword,
  database: process.env.mysqlDB,
};

async function createNewUser(eml, usr, pswd) {
  // const usrs = await User.findOne( {$or: [{ username: usr}, {email:eml}]}).lean();
  var con = mysql.createConnection(sqlConfig);
  var query = "SELECT * FROM User WHERE username = ?";
  let value = [usr];
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
  if (result.length === 0 || !result) {
    // const hashs = bcrypt.hashSync(pswd, hash);
    bcrypt.genSalt(parseInt(process.env.hash), function (err, salt) {
      bcrypt.hash(pswd, salt, function (err, hashs) {
        let query = "INSERT INTO user (email, username, pwd) VALUES ( ?, ?, ?)";
        let values = [eml, usr, hashs];
        con.promise().query(query, values);
      });
    });
  }
  //add error things here
}

var tableData;
var errorTable;
async function fetchTableData() {
  // pull researcher table data from sql db, export it as json response
  var con = mysql.createConnection(sqlConfig);
  var query1 =
    "SELECT Devices.sn, Devices.pmHealth, Devices.sdHealth,Devices.onlne, Devices.dataFraction, CONCAT(ROUND(Devices.dataFraction*100,2),'%') AS dataFraction, Data.pm25, Data.pm10,  SUBSTRING(Data.timestamp,1,10) AS timestamp FROM Devices LEFT JOIN ( SELECT d1.* FROM Data d1 JOIN ( SELECT sn, MAX(timestamp) AS max_timestamp FROM Data GROUP BY sn ) d2 ON d1.sn = d2.sn AND d1.timestamp = d2.max_timestamp ) AS Data ON Data.sn = Devices.sn ORDER BY Devices.sn;";
  await con
    .promise()
    .query(query1)
    .then(([rows, fields]) => {
      tableData = rows;
    })
    .catch((err) => {
      console.error(err);
    });

  var query2 =
    "SELECT Devices.sn, Devices.description, Devices.pmHealth, Devices.sdHealth, Devices.onlne, CONCAT(ROUND(Devices.dataFraction*100,2),'%') AS dataFraction , SUBSTRING(Devices.last_seen,1,10) AS last_seen FROM Devices WHERE Devices.sdHealth = 'ERROR' OR Devices.pmHealth='ERROR' OR Devices.onlne = 'offline' ORDER BY Devices.onlne, Devices.sdHealth DESC, Devices.pmHealth DESC;";

  await con
    .promise()
    .query(query2)
    .then(([rows, fields]) => {
      errorTable = rows;
    })
    .catch((err) => {
      console.error(err);
    });
}
fetchTableData();
var addedResearchers;
async function emailGet() {
  var con = mysql.createConnection(sqlConfig);
  var query = "SELECT email FROM User";
  await con
    .promise()
    .query(query)
    .then(([rows, fields]) => {
      addedResearchers = rows;
    })
    .catch((err) => {
      console.error(err);
    });
}
emailGet();
async function run() {
  try {
    // Connect the client to the server	(optional starting in v4.7)
    // await client.connect();
    // // Send a ping to confirm a successful connection
    // await client.db("SSProject").command({ ping: 1 });
    // console.log("Pinged your deployment. You successfully connected to MongoDB!");
    await createNewUser("tno@gmail.com", "pyTest", "1234");
  } finally {
    // Ensures that the client will close when you finish/error
  }
}
run().catch(console.dir);
// --------------- end of code for connecting to the mongoDB cloud ---------------

// --------------- code for setting up the application ---------------
// dependancies
const express = require("express");
const hbs = require("express-handlebars");
const app = express();
const path = require("node:path");
const session = require("express-session");

app.use(express.json());
//for req and res
app.use(bodyParser.json()); // Parse JSON bodies
app.use(bodyParser.urlencoded({ extended: true }));
// Templating Engine
app.engine(
  "hbs",
  hbs.engine({
    extname: "hbs",
    defaultLayout: "index",
    layoutsDir: __dirname + "/views/layouts/",
  }),
);

app.use(express.static(path.join(__dirname, "public")));

app.set("views", path.join(__dirname, "views"));
app.set("view engine", "hbs");

app.use(
  session({
    secret: "secret",
    resave: true,
    saveUninitialized: true,
  }),
);
// --------------- end of code for setting up the application ---------------

// --------------- code for routing to pages ---------------
// creates home page
const homeRouter = require("./routes/home.js");
app.use("/home", homeRouter);
app.use("", homeRouter);

// creates map page
const mapRouter = require("./routes/map.js");
app.use("/map", mapRouter);

// create route for the researcher table data
app.get("/data", (req, res) => {
  res.json(tableData);
});
app.get("/errorData", (req, res) => {
  res.json(errorTable);
});

app.get("/researcher", async (req, res) => {
  await emailGet();
  // add a security check here
  res.json(addedResearchers);
});

//creates participant login page
const loginRouter = require("./routes/login.js");
app.use("/login", loginRouter);

//creates success page
const successRouter = require("./routes/success-page.js");
app.use("/success-page", successRouter);

///////////////////////////

//viewDataRouter
const viewDataRouter = require("./routes/viewData.js");
app.use("/view-data", viewDataRouter);

//////////////////////
app.route("/invite").post(async (req, res) => {
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB,
  });
  const { email } = req.body;
  var query = "SELECT * FROM User WHERE email = ?";
  let value = [email];
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
  if (result.length !== 0) {
    res.redirect('/invite?error="usrE');
    return;
  }
  const token = jwt.sign({ email: email }, process.env.key, {
    algorithm: "HS256",
    allowInsecureKeySizes: true,
    expiresIn: 7200, // 24 hours
  });
  const registersite = "http://localhost:3000/register?token=";
  const site = registersite + token;
  var data = {
    link: site,
  };
  var message = `
  Hello ${email},

This email is to let you sign up for  your account on the Salton Sea Air Filtration Website.

Please use this link 

${site}

If you have any questions please email Professor Porter.

If you are not a part of his team, please ignore this message.

Best wishes,
EmailJS team
  `;
  // email the message here
  var transport = nodemailer.createTransport({
    host: "sandbox.smtp.mailtrap.io",
    port: 2525,
    auth: {
      user: process.env.mailtrapeuser,
      pass: process.env.mailtrappassword,
    },
  });

  var msg = {
    from: "jchang1211@gmail.com",
    to: "jchan443@ucr.edu",
    subject: "Salton Sea Researcher Registration",
    text: message,
  };
  transport.sendMail(msg);
  console.log(message);

  res.redirect("/invite");
  // emailjs.init({publicKey:process.env.emjs});
  // emailjs.send(process.env.sid, process.env.tempid, data);
});
const inviteRouter = require("./routes/invite.js");
app.use("/invite", inviteRouter);

app.route("/register").post(async (req, res) => {
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB,
  });
  const { token, username, password, retype } = req.body;
  if (!token) {
    res.redirect("/home");
  }
  // const urlParams = new URLSearchParams(window.location.search);
  // const myParam = urlParams.get('myParam');
  // const token = urlParams.get('token')[0];
  var errorpage = "/register?token=" + token + "&error=";
  var haserror = false;
  if (!username) {
    errorpage += "usr2";
    haserror = true;
  }
  var query = "SELECT * FROM User WHERE username = ?";
  let value = [username];
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
  if (result.length !== 0) {
    errorpage += "usr1";
    haserror = true;
  } else {
    if (!password) {
      errorpage += "pw2";
      haserror = true;
    }
    //add regex checking here
    const passwordPattern =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&-])[A-Za-z\d@$!%*?&-]{8,}$/;
    if (!passwordPattern.test(password)) {
      haserror = true;
      errorpage += "pw1";
    }
    if (password != retype) {
      errorpage += "pw3";
      haserror = true;
    }
    if (!haserror) {
      var email;
      jwt.verify(token, process.env.key, (error, decoded) => {
        if (error) {
          haserror = true;
          //  add errors here redirecting
          // res.redirect('/home');
        }
        email = decoded.email;
        console.log(email);
      });
      // const user = await User.findOne({email: email});
      var query = "SELECT * FROM User WHERE username = ?";
      let value = [username];
      var result2;
      await con
        .promise()
        .query(query, value)
        .then(([rows, fields]) => {
          result2 = rows;
        })
        .catch((err) => {
          console.error(err);
        });

      if (result2.length === 0) {
        await createNewUser(email, username, password);
        res.redirect("/rlogin");
      } else {
        res.redirect("/rlogin?error=ngl2");
      }
    }
  }
  if (haserror) {
    res.redirect(errorpage);
  }
});
const registerRouter = require("./routes/register.js");
app.use("/register", registerRouter);

app.route("/rlogin").post(async (req, res) => {
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB,
  });
  const { username, password } = req.body;
  var query = "SELECT * FROM User WHERE username = ?";
  let value = [username];
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
  // const user  = await User.findOne({username: username})
  errorpage = "/rlogin?error=";
  haserror = false;
  if (!username) {
    errorpage += "usr2";
    haserror = true;
  }
  if (result.length === 0) {
    errorpage += "usr1";
    haserror = true;
  } else {
    if (!password) {
      errorpage += "pw2";
      haserror = true;
    }
    var input = result[0].pwd;
    const response = bcrypt.compareSync(password, input);
    if (response == true) {
      if (!haserror) {
        req.session.logged_in = true;
        req.session.token = jwt.sign(
          { username: result[0].username },
          process.env.key,
          {
            algorithm: "HS256",
            allowInsecureKeySizes: true,
            expiresIn: 7200, // 24 hours
          },
        );
        res.redirect("/table");
      }
    }
    if (response == false) {
      errorpage += "pw1";
      haserror = true;
    }
  }

  if (haserror) {
    res.redirect(errorpage);
  }

  // res.redirect('/rlogin?error=pw1')
});

const rloginRouter = require("./routes/rlogin.js");
app.use("/rlogin", rloginRouter);

const tableRouter = require("./routes/table.js");
app.use("/table", tableRouter);
const lgRouter = require("./routes/logout.js");
app.use("/logout", lgRouter);
////////////////////////////////////////////////////////////////

////////////////////////////////////////////////////////////////
const router = express.Router();

app.get("/monitorIds", async (req, res) => {
  try {
    const connection = await pool.promise().getConnection();

    const [rows] = await connection.query("SELECT sn FROM Devices");

    connection.release();

    const monitorIds = rows.map((row) => row.sn);

    res.json({ monitorIds });
  } catch (error) {
    console.error("Error fetching monitor IDs from database:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});
//////////////////////////////////////////////

/*
// fix this
async function fetchAQIData() {
  const result = await new Promise((resolve, reject) => {
    PythonShell.run("data_call/idontfuckingknow.py", options).then((result) => {
      // if (err) {
      //     console.error('Error fetching AQI data:', err);
      //     return;
      // }
      console.log("hello");
      aqiData = JSON.parse(result);
      return aqiData;
    });
  });
}
fetchAQIData();

app.get("/aqiData", async (req, res) => {
  let aqidata = await fetchAQIData();
  console.log(aqidata);
  res.json(aqidata);
});
*/
app.post("/changePMType", async (req, res) => {
  const selectedPMType = req.body.pm_type;
  console.log(selectedPMType);
  let options = {
    mode: "text",
    pythonPath: ".venv/bin/python",

    pythonOptions: ["-u"], // get print results in real-time
    args: [selectedPMType],
  };
  let { PythonShell } = require("python-shell");
  await PythonShell.run("data_call/generateMap.py", options, (err, results) => {
    if (err) throw err;
    console.log("Map generation completed");
  });

  res.redirect("/map"); //redirects back to the map page
});
//Export the router
module.exports = router;
/////////////////////////////////////////////////////////////
// --------------- end of code for routing to pages ---------------

// export to server... important to never remove this from the bottom!
module.exports = app;
