const express = require('express')
const router = express.Router()

router.get('/', (req,res) => {
    
    if (req.session.logged_in) {
        res.render("success-page", { title: 'SUCCESS PAGE ', monitorId : req.query.monitorId });
        res.status(200);
    }
    else {
        res.redirect('/login');
    }

})

module.exports = router;