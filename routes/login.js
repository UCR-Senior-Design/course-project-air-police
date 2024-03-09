const express = require("express");
const router = express.Router();

const validMonitorIds = [
    "948", "1001", "976", "966", "993",
    "1002", "977", "972", "998", "947",
    "953", "1003", "956", "1000", "989",
    "984", "1014", "987", "950", "978",
    "982", "1006", "962", "1021", "346",
    "988", "1015", "992", "999", "983",
    "1020", "967", "965", "973", "979",
    "970", "985", "995", "964", "952",
    "949", "946", "994", "1022", "951",
    "986", "957", "1007", "1023", "963"
];

function checkValid(monitorId) {
    // Check if entered monitor ID is valid
    const isValidMonitorId = validMonitorIds.some(id => monitorId.toUpperCase() === id.toUpperCase());
    return isValidMonitorId;
}

router.get('/', (req,res) => {

    const monitorId = req.query.monitorId;
    console.log("Submitted monitor ID:", monitorId);
    var valid = false;

    if (monitorId != null) {
        valid = checkValid(monitorId)
    }        
    if (valid) {
        res.redirect("/success-page?monitorId=" + monitorId) // sends status code 302 by default
    }
    else {
        res.render("login", { displayText: 'login page' });
        res.status(200); 
    }

})

module.exports = router;