const Chart = require("chart.js");
const { Pool } = require("pg");
const postgreConfig = {
    connectionString: process.env.POSTGRES_URL ,
  };
async function retrieveData(description){
    var result;
    try{
        var pool = new Pool(postgreConfig);
        const con = await pool.connect();
        // offset is by # of hours in a day * #numer of minutes in an hour * number of seconds in a minute * number of millis in a second. then multiplied by the number of days.
        var offset = (24*60*60*1000) * 1;
        var threshold = new Date();
        threshold.setTime(threshold - offset);
        threshstring = threshold.toISOString();
        const query = "SELECT Data.pm25, Data.pm10, timestamp FROM Data, Devices WHERE Data.sn = Devices.sn AND Devices.description = $1 AND timestamp > $2 ORDER BY timestamp";
        const value = [description, threshstring];
        const queryResponse = await con.query(query, value);
        result = queryResponse.rows;
        return result;

    } catch(error){
        console.error("Error regarding Postgres: " + error);
        return null;
    }

}
console.log("hello");
async function generateImage(description){
    try{
    console.log("description is " + description);
    var result = await retrieveData(description);
    }catch(error){
        console.error(error);
    }
    const data = {
        labels: result.map(row=>row.timestamp),
        datasets: [
            {
              label: 'pm2.5',
              borderColor: 'red',
              data: result.map(row=>row.pm25),
              fill: false
            },
            {
              label: 'pm10',
              borderColor: 'blue',
              data: result.map(row=>row.pm10),
              fill: false
            }
        ]
    };
    return data;
}

module.exports = generateImage;