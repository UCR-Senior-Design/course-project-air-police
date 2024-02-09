// --------------- code for connecting to the mongoDB cloud ---------------

require('dotenv').config()
const mg = require('mongoose');
const { MongoClient, ServerApiVersion } = require('mongodb');
const User = require("./models/user.js")
const bodyParser = require('body-parser')
var bcrypt = require('bcryptjs');
var jwt = require('jsonwebtoken');
const hash = process.env.hash;
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
  const usrs = await User.findOne( {$or: [{ username: usr}, {email:eml}]}).lean();
  if(!usrs){
    // const hashs = bcrypt.hashSync(pswd, hash);
    bcrypt.genSalt(parseInt(process.env.rounds_num), function(err, salt) {
      bcrypt.hash(pswd, salt, function(err, hashs) {
        const test =  new User({ 
          email: eml,
          username: usr,
          password: hashs
        });
        test.save();
      });
  });
    
  }
  //add error things here
}

async function run() {
  try {
    // Connect the client to the server	(optional starting in v4.7)
    // await client.connect();
    await mg.connect(process.env.DATABASE_URL)
    // // Send a ping to confirm a successful connection
    // await client.db("SSProject").command({ ping: 1 });
    // console.log("Pinged your deployment. You successfully connected to MongoDB!");
    await createNewUser('pyTest','1234');
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
//////////

///////////////////////////

//viewDataRouter
const viewDataRouter = require('./routes/viewData.js');
app.use('/view-data', viewDataRouter);

//////////////////////
app.route('/invite').post( async (req, res) =>{
  
  const {email} = req.body;
  const user = await User.findOne({email:email});
  if(user){
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
  console.log(message);
  res.redirect('/invite');
  // emailjs.init({publicKey:process.env.emjs});
  // emailjs.send(process.env.sid, process.env.tempid, data);
})
const inviteRouter = require('./routes/invite.js');
app.use('/invite',inviteRouter);

app.route('/register').post( async (req, res) => {
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
  const user = await User.findOne({username:username});
  if(user){
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
      const user = await User.findOne({email: email});
      if(!user){
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
  const {username, password} = req.body;
  const user  = await User.findOne({username: username})
  errorpage = '/rlogin?error='
  haserror = false;
  if(!username){
    errorpage+= 'usr2'
    haserror = true
  }
  if(!user){
    errorpage += 'usr1';
    haserror = true;
  } 
  else {
    if(!password){
      errorpage += 'pw2';
      haserror = true;
    }
      const response =  bcrypt.compareSync(password,user.password)
        if(response == true){
          if(!haserror){
            req.session.logged_in = true
            req.session.token = jwt.sign({username: user.username}, process.env.key,{
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

//Export the router
module.exports = router;
/////////////////////////////////////////////////////////////
// --------------- end of code for routing to pages ---------------


// export to server... important to never remove this from the bottom!
module.exports = app;