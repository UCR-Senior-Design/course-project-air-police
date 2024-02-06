const express = require('express')
const router = express.Router()

// Getting all
router.get('/', (req,res) => {
    if(req.session.logged_in){
        res.render('table', {
            title: 'AirPolice Map',
            body: 'success'
        });
        res.sendStatus(200); 
    }
    else{
        res.redirect('/rlogin?error=ngl');
        res.sendStatus(400); 
    }
})


module.exports = router