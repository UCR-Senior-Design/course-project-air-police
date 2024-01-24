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


async function createNewUser(usr, pswd){
  const usrs = await User.findOne({ username: usr}).lean();
  if(!usrs){
    // const hashs = bcrypt.hashSync(pswd, hash);
    bcrypt.genSalt(hash, function(err, salt) {
      bcrypt.hash(pswd, salt, function(err, hashs) {
        const test =  new User({ 
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

//creates provisional in-progress data viewing page
const viewDataRouter = require('./routes/viewData.js')
app.use('/view-data', viewDataRouter);

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
            req.session.token = jwt.sign({user: user.username}, process.env.private_key);
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
// --------------- end of code for routing to pages ---------------


// export to server... important to never remove this from the bottom!
module.exports = app;