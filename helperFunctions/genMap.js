const {Pool} = require("pg");

const postgreConfig = {
    connectionString: process.env.POSTGRES_URL ,
  };


function calculateAverage(data){
    var sum = 0;
    var length = data.length
    for(var i = 0; i < data.length; i++){
        if(Number(data[i]) === 0){
            length = length - 1;
            continue;
        }else{
            sum += Number(data[i]);
        }
    }

    return sum / length;
}
async function grabData(pm_type){
    try{
        var pool = new Pool(postgreConfig);
        const con = await pool.connect();
        var query = ""
        if(pm_type = "pm25"){
            query = "SELECT Devices.sn, Devices.lat, Devices.lon, Data.pm25, Data.pm10, Data.timestamp FROM Devices LEFT JOIN ( SELECT d1.* FROM Data d1 JOIN ( SELECT sn, MAX(timestamp) AS max_timestamp FROM Data GROUP BY sn ) d2 ON d1.sn = d2.sn AND d1.timestamp = d2.max_timestamp ) AS Data ON Data.sn = Devices.sn ORDER BY Devices.sn;"
        } else{
            query = "SELECT Devices.sn, Devices.lat, Devices.lon, Data.pm10, Data.pm25, Data.timestamp FROM Devices LEFT JOIN ( SELECT d1.* FROM Data d1 JOIN ( SELECT sn, MAX(timestamp) AS max_timestamp FROM Data GROUP BY sn ) d2 ON d1.sn = d2.sn AND d1.timestamp = d2.max_timestamp ) AS Data ON Data.sn = Devices.sn ORDER BY Devices.sn";
        }
        const result = await con.query(query);
        const queryResult = result.rows;
        return queryResult;
    } catch(error){
        console.error("Error Fetching from dataBase: " + error );
    }
};

async function genData(pm_type){
    // get most recent data here
    var data = await grabData(pm_type);
    const lat = data.map(rows => rows.lat);
    const lon = data.map(rows => rows.lon);
    console.log(lat);
    const central_lat = calculateAverage(lat);
    console.log(central_lat);
    const central_lon = calculateAverage(lon);
    return {data, central_lat, central_lon};
    // var map = L.map('map').setView([central_lat, central_lon],20);
    // L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    //     attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions">CARTO</a>',
    //     subdomains: 'abcd',
    //     maxZoom: 21
    // }).addTo(map);
}

module.exports = genData;