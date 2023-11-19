
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

const express = require('express')
const app = express()
app.use(express.json())

// creates homePage
const homeRouter = require('./routes/home')
app.use('/home', homeRouter)

app.listen(3000, () => console.log('Server Started'))



// --------------- end of code for routing to pages ---------------
