const express = require('express')
const router = express.Router()

router.get('/', (req, res) => {
  // if(req.session.logged_in){
  //   res.redirect('/table') // sends status code 302 by default
  // }else{
    res.render('rlogin', { title: 'LOGIN ', displayText: 'researcher login test' });
    res.status(200); 
})
module.exports = router