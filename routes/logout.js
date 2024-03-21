const express = require("express");
const router = express.Router();

router.get("/", (req, res) => {
  req.session.logged_in = false;
  req.session.token = "";
  res.redirect("/home");
});
module.exports = router;
