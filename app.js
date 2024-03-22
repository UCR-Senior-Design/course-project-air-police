// --------------- code for connecting to the database ---------------

require("dotenv").config();
const bodyParser = require("body-parser");
var bcrypt = require("bcryptjs");
var jwt = require("jsonwebtoken");
const nodemailer = require("nodemailer");
const hash = process.env.hash;
const { Pool } = require("pg");
// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const { request } = require("http");
const postgreConfig = {
  connectionString: process.env.POSTGRES_URL
};

async function createNewUser(eml, usr, pswd) {
  try{
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    var query = "SELECT * FROM usrs WHERE username = $1 ";
    let value = [usr];
    var result;
    result = await con.query(query, value);
    
    if (result.rows.length === 0 || !result) {
      // const hashs = bcrypt.hashSync(pswd, hash);
      bcrypt.genSalt(parseInt(process.env.hash), function (err, salt) {
        bcrypt.hash(pswd, salt, function (err, hashs) {
          try{
          let query =
            "INSERT INTO usrs (email, username, pwd) VALUES ( $1, $2, $3);";
          let values = [eml, usr, hashs];
          con.query(query, values);
          }
          catch(error){
            console.error(error);
          }
          
        });
      });
    }
  }catch(error){
    console.error(error);
  }


    // await con.end();
  //add error things here
}
createNewUser("tno@gmail.com", "pyTest", "1234");
var tableData;
var errorTable;
async function fetchTableData() {
  // pull researcher table data from sql db, export it as json response
  try {
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    var query1 =
      "SELECT Devices.sn, Devices.pmhealth, Devices.sdhealth,Devices.onlne, CONCAT(ROUND(Devices.datafraction*100,2),'%') AS datafraction, Data.pm25, Data.pm10,  SUBSTRING(Data.timestamp,1,10) AS timestamp FROM Devices LEFT JOIN ( SELECT d1.* FROM Data d1 JOIN ( SELECT sn, MAX(timestamp) AS max_timestamp FROM Data GROUP BY sn ) d2 ON d1.sn = d2.sn AND d1.timestamp = d2.max_timestamp ) AS Data ON Data.sn = Devices.sn ORDER BY Devices.sn;";
    var result = await con.query(query1);
    // if (result) {
      tableData = result.rows;
    // }
    var query2 =
      "SELECT Devices.sn, Devices.description, Devices.pmhealth, Devices.sdhealth, Devices.onlne, CONCAT(ROUND(Devices.datafraction*100,2),'%') AS datafraction , SUBSTRING(Devices.last_seen,1,10) AS last_seen FROM Devices WHERE Devices.sdHealth = 'ERROR' OR Devices.pmHealth='ERROR' OR Devices.onlne = 'offline' ORDER BY Devices.onlne, Devices.sdHealth DESC, Devices.pmHealth DESC;";
    result = await con.query(query2);
    errorTable = result.rows;
    await con.release();
  } catch (error) {
    console.error(error);
  }
}
// fetchTableData();
var addedResearchers;
async function emailGet() {
  try {
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    var query = "SELECT email FROM usrs";
    var result = await con.query(query);
    addedResearchers = result.rows;
    await con.release();
  } catch (error) {
    console.error(error);
  }
}
emailGet();
async function run() {
  try {
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
app.get("/data",  async (req, res) => {
  await fetchTableData();
  res.json(tableData);
});
app.get("/errorData", async (req, res) => {
  await fetchTableData();
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

//creates participant page
const participantRouter = require("./routes/participant.js");
app.use("/participant", participantRouter);

///////////////////////////


//////////////////////
app.route("/invite").post(async (req, res) => {
  try {
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    const { email } = req.body;
    var query = "SELECT * FROM usrs WHERE email = $1";
    let value = [email];
    var result;

    result = await con.query(query, value);
    if (result.rows.length !== 0) {
      await con.release();
      res.redirect('/invite?error="usrE');
      return;
    }
    await con.release();
  } catch (error) {
    console.error(error);
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
  try {
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    const { token, username, password, retype } = req.body;
    if (!token) {
      res.redirect("/home");
    }

    var errorpage = "/register?token=" + token + "&error=";
    var haserror = false;
    if (!username) {
      errorpage += "usr2";
      haserror = true;
    }
    var query = "SELECT * FROM usrs WHERE username = $1";
    let value = [username];
    var result;

    result = await con.query(query, value);
    if (result.rows.length !== 0) {
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
        // wtf is this shit
        var query = "SELECT * FROM usrs WHERE email = $1";
        let value = [email];
        var result2;
        result2 = await con.query(query, value);

        if (result2.rows.length === 0) {
          await con.release();
          await createNewUser(email, username, password);
          res.redirect("/rlogin");
        } else {
          await con.release();
          res.redirect("/rlogin?error=ngl2");
        }
      }
    }
    if (haserror) {
      res.redirect(errorpage);
    }
  } catch (error) {
    console.error(error);
  }
});
const registerRouter = require("./routes/register.js");
app.use("/register", registerRouter);



app.route("/rlogin").post(async (req, res) => {
  
  try {
    // await createNewUser("tno@gmail.com", "pyTest", "1234");
    var pool = new Pool(postgreConfig);
    const con = await pool.connect();
    await fetchTableData();
    const { username, password } = req.body;
    var query = "SELECT * FROM usrs WHERE username = $1";
    let value = [username];
    var result;

    result = await con.query(query, value);
    errorpage = "/rlogin?error=";
    haserror = false;
    if (!username) {
      errorpage += "usr2";
      haserror = true;
    }
    if (result.rows.length === 0) {
      errorpage += "usr1";
      haserror = true;
    } else {
      if (!password) {
        errorpage += "pw2";
        haserror = true;
      }
      var input = result.rows[0].pwd;
      console.log(input);
      const response = bcrypt.compareSync(password, input);
      if (response == true) {
        // console.log(true);
        if (!haserror) {
          token = jwt.sign(
            { username: result.rows[0].username },
            process.env.key,
            {
              algorithm: "HS256",
              allowInsecureKeySizes: true,
              expiresIn: 7200, // 24 hours
            },
          );
          res.setHeader('Set-Cookie', `token=${token}; Path=/; HttpOnly; SameSite=Strict`);
          await con.release();
          res.redirect("/table");
        }
      }
      if (response == false) {
        errorpage += "pw1";
        haserror = true;
      }
    }

    if (haserror) {
      await con.release();
      res.redirect(errorpage);
    }
  } catch (error) {
    console.error(error);
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
    var pool = new Pool(postgreConfig);
    const connection = await pool.connect();
    const result = await connection.query("SELECT sn FROM Devices");
    const [rows] = result.rows;

    connection.release();

    const monitorIds = rows.map((row) => row.sn);

    res.json({ monitorIds });
  } catch (error) {
    console.error("Error fetching monitor IDs from database:", error);
    res.status(500).json({ error: "Internal server error" });
  }
});
//////////////////////////////////////////////

const pullData = require("./helperFunctions/pullData.js");
app.post("/pushData", async (req, res)=>{
  await pullData();
  res.send({"message": "DataBase updated"});
})
const {getID, changeMap} = require('./routes/changepm.js')
app.post("/changePMType", async (req, res) => {
  const selectedPMType = req.body.pm_type;
  changeMap(selectedPMType);
  res.redirect("/map"); //redirects back to the map page
});

app.post("/chart", async (req, res)=>{
  const sn = req.body.sn;
  // // do a function here to get base64
  //this do not work
  // var img_src = await genChart(sn);
  // var img = {link: img}
  // res.json(img);
})

//Export the router
module.exports = router;
/////////////////////////////////////////////////////////////
// --------------- end of code for routing to pages ---------------

// export to server... important to never remove this from the bottom!
module.exports = app;
