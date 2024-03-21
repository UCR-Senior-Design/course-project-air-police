const {Pool} = require("pg");
const postgreConfig = {
    connectionString: process.env.POSTGRES_URL ,
  };
function genMap(pm_type){
    // get most recent data here
    var data;
    const central_lat = 1;
    const central_lon = 1;
}