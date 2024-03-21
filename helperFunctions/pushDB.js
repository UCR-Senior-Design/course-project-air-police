const { Pool } = require("pg");
const http = require('http');
const apiKey = process.env.apiKey;
const postgreConfig = {
    connectionString: process.env.POSTGRES_URL ,
};

async function connecttoAPI(sn){
// Define the options for the HTTP request
    const today =new Date().toISOString().split('T')[0];
    const options = {
        hostname: 'api.quant-aq.com',
        path: "/device-api/v1/devices/" + sn + "/data-by-date/" + today,
        method: 'GET',
        headers: {
            'Authorization': `Basic ${Buffer.from(apiKey + ':').toString('base64')}`
        }
    };

    // Create a new HTTP request
    const req = http.request(options, (res) => {
        let data = '';

        // Collect response data as it comes in
        res.on('data', (chunk) => {
            data += chunk;
        });

        // When response is complete, handle the data
        res.on('end', () => {
            if (res.statusCode === 200) {
                // Request successful, parse response data if needed
                const jsonData = JSON.parse(data);
                return jsonData;
            } else {
                console.error('Error:', res.statusCode, res.statusMessage);
            }
        });
    });
    // Handle errors with the request
    req.on('error', (error) => {
        console.error('Error:', error.message);
    });

    // Send the request
    req.end();
}

async function pushDB(){
    try{
        var pool = new Pool(postgreConfig);
        const con = await pool.connect();
        var query = "SELECT sn FROM Devices";
        const result = await con.query(query);
        const rows = result.rows;
        query = "INSERT INTO Data (sn, pm25, pm10, timestamp) VALUES ($1,$2,$3,$4) ON CONFLICT (sn,timestamp) DO UPDATE SET pm25 = EXCLUDED.pm25, pm10= EXCLUDED.pm10"
        rows.forEach(async (sn, index)=>{
            const data =  await connecttoAPI(sn);
            console.log(data);
            // values = []
            // await con.query(query,)
        });
    }catch(error){
        console.log(error);
    }
}