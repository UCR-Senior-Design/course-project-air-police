const Plotly = require('plotly');
const { Pool } = require("pg");

const postgreConfig = {
    connectionString: process.env.POSTGRES_URL ,
  };
async function generateImage(description){
    var result;
    try{
        var pool = new Pool(postgreConfig);
        const con = await pool.connect();
        // offset is by # of hours in a day * #numer of minutes in an hour * number of seconds in a minute * number of millis in a second. then multiplied by the number of days.
        var offset = (24*60*60*1000) * 15;
        var threshold = new Date();
        threshold.setTime(threshold - offset);
        threshstring = threshold.toISOString();
        const query = "SELECT Data.pm25, Data.pm10, timestamp FROM Data, Devices WHERE Data.sn = Devices.sn AND Devices.description = $1 AND timestamp > $2 ORDER BY timestamp";
        const value = [description, threshstring];
        const queryResponse = await con.query(query, value);
        result = queryResponse.rows;

    } catch(error){
        console.error("Error regarding Postgres: " + error);
    }

    const pm25line = [{
        type:"scatter",
        mode:"lines",
        name:"pm25",
        x:result.map(row => row.timestamp),
        y:result.map(row => row.pm25),
        line: {color:"#17fce9"}
    }];
    const pm10line = [{
        type:"scatter",
        mode:"lines",
        name:"pm10",
        x:result.map(row => row.timestamp),
        y:result.map(row => row.pm10),
        line: {color:"##8500fa"}
    }];
    var data = [pm25line, pm10line];
    const layout = {
        title: `Time series for ${description}`,
        xaxis: {
            title: 'timestamp'
        },
        yaxis: {
            title: 'pm Value'
        }
    };
    var base64str = "images/refresh.png";
    try{
    const plot = await Plotly.newPlot('pmvalue', data, layout);
    base64str = await plot.toImage({ format: 'png', width: 800, height: 600 })
    }catch(error){
        console.error("Error creating the chart" + error);
    }
    return base64str;
}

module.exports = generateImage;