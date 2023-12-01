const express = require('express')
const router = express.Router()

// Getting all
router.get('/', (req,res) => {
    if(req.session.logged_in){
        res.render('test', {
            title: 'AirPolice Map',
            body: 'success'
        });
    }
    else{
        res.redirect('/rlogin?error=ngl');
    }
})


module.exports = router