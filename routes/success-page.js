const express = require('express')
const router = express.Router()

router.get('/', (req,res) => {
    
    res.render("success-page", { title: 'SUCCESS PAGE ', monitorId : req.query.monitorId });
    res.status(200);
})

module.exports = router;