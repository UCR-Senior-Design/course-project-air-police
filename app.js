
// --------------- code for connecting to the mongoDB cloud ---------------

require('dotenv').config()

const { MongoClient, ServerApiVersion } = require('mongodb');

// Create a MongoClient with a MongoClientOptions object to set the Stable API version
const client = new MongoClient(process.env.DATABASE_URL, {
  serverApi: {
    version: ServerApiVersion.v1,
    strict: true,
    deprecationErrors: true,
  }
});

async function run() {
  try {
    // Connect the client to the server	(optional starting in v4.7)
    await client.connect();
    // Send a ping to confirm a successful connection
    await client.db("admin").command({ ping: 1 });
    console.log("Pinged your deployment. You successfully connected to MongoDB!");
  } finally {
    // Ensures that the client will close when you finish/error
    await client.close();
  }
}
run().catch(console.dir);

// --------------- end of code for connecting to the mongoDB cloud ---------------

// --------------- code for routing to pages ---------------

// dependancies
const express = require('express')
const hbs = require('express-handlebars');
const app = express()
const path = require('node:path');

app.use(express.json())

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

//app.use(express.static('public')); // apparently easier to acccess this way
//app.set('index', './layouts/home')


// creates homePage
const homeRouter = require('./routes/home.js')
app.use('/home', homeRouter)



// --------------- end of code for routing to pages ---------------

app.get('', (req,res) => {
    res.send("On main web page from app.js");
});

// export to server... important to never remove this from the bottom!
module.exports = app;
