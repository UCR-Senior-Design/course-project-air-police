const express = require('express')
const router = express.Router()

router.get('/', (req, res) => {
  res.render('rlogin', { title: 'LOGIN ', displayText: 'researcher login test' });
})

module.exports = router