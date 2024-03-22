const { Pool } = require("pg");
const http = require('http');
const apiKey = process.env.api_key;

const headers = {
    'Authorization': `Basic ${Buffer.from(apiKey + ':').toString('base64')}`,
    'Content-Type': 'application/json' // Adjust content type if needed
  };
  

const postgreConfig = {
    connectionString: process.env.POSTGRES_URL ,
};




async function grabsnLastSeen(){
    try{
        var pool = new Pool(postgreConfig);
        const con = await pool.connect();
        const query = "SELECT sn, last_seen FROM Devices;"
        const rows = await con.query(query);
        const data = rows.rows;
        con.release();
        return data;
    } catch(error){
        console.error("Error Pulling from db: " + error);
    }
}
async function pullSpecific(serialNumber, last_seen){
    const date = last_seen.split("T")[0]
    const url = `https://api.quant-aq.com/device-api/v1/devices/${serialNumber}/data-by-date/${date}`
    console.log(url)
    const list = await fetch(url, {method:'GET', headers: headers})
    .then( response =>{
        if(!response.ok){
            throw new Error("Error Fetching Response: Network Response Not OK");
        }
        return response.json();
    })
    .then( data =>{
        return data.data;
    })
    .catch( error => {
        console.error("Fetch Operation failed: " + error);
        return null;
    });
    return list;
}


async function quer(query, values) {
    try {
        const pool = new Pool(postgreConfig);
        const con = await pool.connect();

        // Ensure values is an array
        const params = Array.isArray(values) ? values : [values];

        await con.query(query, params);
        await con.release();
    } catch (error) {
        console.error("Error pushing to DB: " + error);
    }
}

// had to get it optimize it through batches
async function pullData() {
    var data = await grabsnLastSeen();

    // Set a batch size for batch inserts
    const batchSize = 250;
    const dataLength = data.length;

    for (let i = 0; i < dataLength; i++) {
        try {
            const list = await pullSpecific(data[i].sn, data[i].last_seen);
            if (!list) {
                continue;
            }

            const rows = list.map(row => [row.sn, row.pm25, row.pm10, row.timestamp]);

            // Batch insert into the database
            for (let j = 0; j < rows.length; j += batchSize) {
                const batchRows = rows.slice(j, j + batchSize);

                // Prepare placeholders for parameterized query
                const placeholders = batchRows.map((row, index) => `($${index * 4 + 1}, $${index * 4 + 2}, $${index * 4 + 3}, $${index * 4 + 4})`).join(',');

                // Generate parameterized query
                const query = `INSERT INTO Data (sn, pm25, pm10, timestamp) VALUES ${placeholders} ON CONFLICT (sn, timestamp) DO UPDATE SET pm25 = EXCLUDED.pm25, pm10 = EXCLUDED.pm10`;

                

                // Flatten batchRows to pass as parameters
                const flatBatchRows = batchRows.reduce((acc, val) => acc.concat(val), []);

                // Execute the batch insert query
                await quer(query, flatBatchRows);
            }

            console.log(`Inserted ${rows.length} rows into database on index ${i} out of ${dataLength}`);
        } catch (error) {
            console.error("Error loading data: " + error);
        }
    }
}


module.exports = pullData;