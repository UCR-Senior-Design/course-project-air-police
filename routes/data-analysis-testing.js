const express = require("express");
const router = express.Router();

router.get('/', (req,res) => {
    const monitorId = req.body.monitorId;
    //For now, let's just render a page that displays a monitor ID prompt
    res.render("data-analysis-testing", { displayText: 'analysis login test' });

    // // do something like this
    // if(req.session.logged_in){
    //     res.redirect('/table') // sends status code 302 by default
    //   }else{
    //     res.render('rlogin', { title: 'LOGIN ', displayText: 'researcher login test' });
    //     res.status(200); 
    //   }

})

module.exports = router;