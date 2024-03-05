const express = require('express')
const router = express.Router()

router.get('/data-analysis-testing', (req,res) => {
    const monitorId = req.body.monitorId;

    //For now, let's just render a page that displays a monitor ID prompt
    res.render("data-analysis", { monitorId: monitorId });
})

module.exports = router;