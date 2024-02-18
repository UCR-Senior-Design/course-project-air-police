// --------------- code for connecting to the database ---------------

require('dotenv').config()
const mg = require('mongoose');
const { MongoClient, ServerApiVersion } = require('mongodb');
const User = require("./models/user.js")
const bodyParser = require('body-parser')
var bcrypt = require('bcryptjs');
var jwt = require('jsonwebtoken');
const nodemailer = require('nodemailer');
const hash = process.env.hash;
const mysql = require('mysql2');
// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(process.env.DATABASE_URL, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
});
const { request } = require('http')


async function createNewUser(eml, usr, pswd){
  // const usrs = await User.findOne( {$or: [{ username: usr}, {email:eml}]}).lean();
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB 
  });
  var query = "SELECT * FROM User WHERE username = ?";
  let value = [usr]
  var result;
  await con.promise().query(query, value)
      .then(([rows, fields]) => {
          result = rows;
      })    
      .catch((err) => {
          console.error(err);
       });
  if(result.length === 0 || !result){
    // const hashs = bcrypt.hashSync(pswd, hash);
    bcrypt.genSalt(parseInt(process.env.hash), function(err, salt) {
      bcrypt.hash(pswd, salt, function(err, hashs) {
        let query = "INSERT INTO user (email, username, pwd) VALUES ( ?, ?, ?)";
        let values = [eml, usr, hashs]
        con.promise().query(query, values);
      });
  });
    
  }
  //add error things here
}

	// // Specify the JSON data to be displayed 
	// var tableData = 
	// [ 
	// 	{ 
	// 	"sn": "12345", 
	// 	"pm25": "12345", 
	// 	"pm10": "12345" ,
  //   "timestamp": "00000000"
	// 	}, 
	// 	{ 
  //     "sn": "12345", 
  //     "pm25": "12345", 
  //     "pm10": "12345" ,
  //     "timestamp": "00000000"
	// 	}, 
	// 	{ 
  //     "sn": "12345", 
  //     "pm25": "12345", 
  //     "pm10": "12345" ,
  //     "timestamp": "00000000"
	// 	}, 
	// 	{ 
  //     "sn": "12345", 
  //     "pm25": "12345", 
  //     "pm10": "12345" ,
  //     "timestamp": "00000000"
	// 	}, 
	// 	{ 
  //     "sn": "12345", 
  //     "pm25": "12345", 
  //     "pm10": "12345" ,
  //     "timestamp": "00000000"
	// 	} 
	// ]; 

var tableData;
async function fetchTableData() {
  // pull researcher table data from sql db, export it as json response
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB 
  });
  var query = "SELECT * FROM Data";
  await con.promise().query(query, value)
      .then(([rows, fields]) => {
          console.log(rows)
          tableData = rows;
      })    
      .catch((err) => {
          console.error(err);
       });
}


async function run() {
  try {
    // Connect the client to the server	(optional starting in v4.7)
    // await client.connect();
    await mg.connect(process.env.DATABASE_URL)
    // // Send a ping to confirm a successful connection
    // await client.db("SSProject").command({ ping: 1 });
    // console.log("Pinged your deployment. You successfully connected to MongoDB!");
    await createNewUser('tno@gmail.com','pyTest','1234');
  } finally {
    // Ensures that the client will close when you finish/error
    await client.close();
  }
}
run().catch(console.dir);
// --------------- end of code for connecting to the mongoDB cloud ---------------


// --------------- code for setting up the application ---------------
// dependancies
const express = require('express')
const hbs = require('express-handlebars');
const app = express()
const path = require('node:path');
const session = require('express-session')

app.use(express.json())
//for req and res
app.use(bodyParser.json()); // Parse JSON bodies
app.use(bodyParser.urlencoded({ extended: true }));
// Templating Engine 
app.engine(
  'hbs',
  hbs.engine({
    extname: 'hbs',
    defaultLayout: 'index',
    layoutsDir: __dirname + '/views/layouts/'
  })
)

app.use(express.static(path.join(__dirname, 'public'))) 

app.set('views', path.join(__dirname, 'views'))
app.set('view engine', 'hbs')

app.use(
  session({
    secret: 'secret',
    resave: true,
    saveUninitialized: true
  })
)
// --------------- end of code for setting up the application ---------------


// --------------- code for routing to pages ---------------
// creates home page
const homeRouter = require('./routes/home.js')
app.use('/home', homeRouter)
app.use('', homeRouter)


// creates map page
const mapRouter = require('./routes/map.js')
app.use('/map', mapRouter)


app.get('/work-in-progress', (req, res) => {
  res.render('work-in-progress', {
      title: 'Work in Progress'
  });
});

// create route for the researcher table data
app.get('/data', (req, res) => {
  res.json(tableData);
});



//creates data analysis testing page
app.get('/data-analysis-testing', (req, res) => {

  //res.send('This is the data analysis testing page');
  res.render('data-analysis-testing');
});

//////////

///////////////////////////

//viewDataRouter
const viewDataRouter = require('./routes/viewData.js');
app.use('/view-data', viewDataRouter);

//////////////////////
app.route('/invite').post( async (req, res) =>{
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB 
  });
  const {email} = req.body;
  var query = "SELECT * FROM User WHERE email = ?";
  let value = [email]
  var result;
  await con.promise().query(query, value)
      .then(([rows, fields]) => {
          result = rows;
      })    
      .catch((err) => {
          console.error(err);
       });
  if(result.length !== 0){
    res.redirect('/invite?error="usrE');
    return;
  }
  const token = jwt.sign({ email: email },
    process.env.key,
    {
      algorithm: 'HS256',
      allowInsecureKeySizes: true,
      expiresIn: 7200, // 24 hours
    });
  const registersite = "http://localhost:3000/register?token=";
  const site = registersite + token;
  var data = {
    link: site
  }
  var message = `
  Hello ${email},

This email is to let you sign up for  your account on the Salton Sea Air Filtration Website.

Please use this link 

${site}

If you have any questions please email Professor Porter.

If you are not a part of his team, please ignore this message.

Best wishes,
EmailJS team
  `
  // email the message here
  var transport = nodemailer.createTransport({
    host: "sandbox.smtp.mailtrap.io",
    port: 2525,
    auth: {
      user: process.env.mailtrapeuser,
      pass: process.env.mailtrappassword,
    }
  });
  
  var msg = {
    from: "jchang1211@gmail.com",
    to: "jchan443@ucr.edu",
    subject: "Salton Sea Researcher Registration",
    text: message
  };
  transport.sendMail(msg)
  res.redirect('/invite');
  // emailjs.init({publicKey:process.env.emjs});
  // emailjs.send(process.env.sid, process.env.tempid, data);
})
const inviteRouter = require('./routes/invite.js');
app.use('/invite',inviteRouter);

app.route('/register').post( async (req, res) => {
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB 
  });
  const {token, username, password, retype} = req.body;
  if(!token){
    res.redirect('/home');
  }
  // const urlParams = new URLSearchParams(window.location.search);
  // const myParam = urlParams.get('myParam');
  // const token = urlParams.get('token')[0];
  var errorpage = "/register?token=" + token + "&error="
  var haserror = false;
  if(!username){
    errorpage+='usr2';
    haserror = true;
  }
  var query = "SELECT * FROM User WHERE username = ?";
  let value = [username]
  var result;
  await con.promise().query(query, value)
      .then(([rows, fields]) => {
          result = rows;
      })    
      .catch((err) => {
          console.error(err);
       });
  if(result.length !== 0){
    errorpage+= 'usr1';
    haserror = true;
  }
  else{
    if(!password){
      errorpage+= 'pw2';
      haserror = true;
    }
    //add regex checking here
    const passwordPattern = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&-])[A-Za-z\d@$!%*?&-]{8,}$/;
    if(!passwordPattern.test(password)){
      haserror = true;
      errorpage += 'pw1';
    }
    if(password != retype){
      errorpage += 'pw3';
      haserror = true;
    }
    if(!haserror){
      var email;
      jwt.verify(token, 
        process.env.key,
        (error, decoded)=>{
          if(error){
            haserror = true;
            //  add errors here redirecting
            // res.redirect('/home');
          }
          email = decoded.email;
          console.log(email);
        });
      // const user = await User.findOne({email: email});
      var query = "SELECT * FROM User WHERE username = ?";
      let value = [username]
      var result2;
      await con.promise().query(query, value)
          .then(([rows, fields]) => {
              result2 = rows;
          })    
          .catch((err) => {
              console.error(err);
           });

      if(result2.length === 0){
        await createNewUser(email, username, password);
        res.redirect('/rlogin');
      }
      else{
        res.redirect('/rlogin?error=ngl2');
      }
    }
  }
  if(haserror){
    res.redirect(errorpage);
  }
})
const registerRouter = require('./routes/register.js');
app.use('/register',registerRouter);


app.route('/rlogin').post( async (req,res) => {
  var con = mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB 
  });
  const {username, password} = req.body;
  var query = "SELECT * FROM User WHERE username = ?";
  let value = [username]
  var result;
  await con.promise().query(query, value)
      .then(([rows, fields]) => {
          result = rows;
      })    
      .catch((err) => {
          console.error(err);
       });
  // const user  = await User.findOne({username: username})
  errorpage = '/rlogin?error='
  haserror = false;
  if(!username){
    errorpage+= 'usr2'
    haserror = true
  }
  if(result.length === 0){
    errorpage += 'usr1';
    haserror = true;
  } 
  else {
    if(!password){
      errorpage += 'pw2';
      haserror = true;
    }
      var input = result[0].pwd;
      const response =  bcrypt.compareSync(password,input)
        if(response == true){
          if(!haserror){
            req.session.logged_in = true
            req.session.token = jwt.sign({username: result[0].username}, process.env.key,{
              algorithm: 'HS256',
              allowInsecureKeySizes: true,
              expiresIn: 7200, // 24 hours
            });
            res.redirect('/table');
          }
        }
        if(response == false){
          errorpage += 'pw1'
          haserror = true;
        }
    }
    
    if(haserror){
      res.redirect(errorpage)
    }
  
  // res.redirect('/rlogin?error=pw1')
});

const rloginRouter = require('./routes/rlogin.js');
app.use('/rlogin',rloginRouter);

const tableRouter = require('./routes/table.js');
app.use('/table',tableRouter);

////////////////////////////////////////////////////////////////
const router = express.Router();

//route for the provisional page
router.get('/work-in-progress', (req, res) => {
    res.render('work-in-progress', {
        title: 'Work in Progress'
    });
});

//Route for handling form submission for data analysis testing
app.post('/data-analysis-testing', (req, res) => {
  const monitorId = req.body.monitorId; 

  //For now, let's just render a page that displays a monitor ID prompt
  res.render('data-analysis', { monitorId: monitorId });
});



//Export the router
module.exports = router;
/////////////////////////////////////////////////////////////
// --------------- end of code for routing to pages ---------------


// export to server... important to never remove this from the bottom!
module.exports = app;