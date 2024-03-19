var entryID = "pm10";
function changeMap(pmtype){
  entryID = pmtype
  return entryID
}
function getID(){
    return entryID
}

module.exports = {getID, changeMap};