const express = require('express')
const router = express.Router()

router.get('/', (req,res) => {
    

    //For now, let's just render a page that displays the success
    res.render("success-page", { title: 'SUCCESS PAGE ', displayText: 'participant login test' });
    res.status(200);
})

module.exports = router;