const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
router.get('/', async (req, res) => {
    var token = req.session.token;
    var username;
    if(!token){
        res.redirect('/table');
    }
    else{
        console.log(token);
        jwt.verify(token, process.env.key, (error, decoded)=>{
            if(error){
                console.error(error);
            }
            username = decoded.username;
        });
        if(username === process.env.porterUser){
            res.render('invite', { title: 'LOGIN ', displayText: 'researcher login test' });
        }
        else{
            res.redirect('/table');
        }
    }
})
module.exports = router