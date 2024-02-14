const express = require('express');
const router = express.Router();

router.get('/view-data', (req, res) => {
   res.render('text-display', { title: 'Text Display Page', displayText: 'This is (provisionally) where the users will access the login page to enter their secure login and view data' });
   res.status(200);
});

module.exports = router;
