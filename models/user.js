const mongoose = require('mongoose')

const Schema = mongoose.Schema
const userSchema = new Schema({
  email: {
    type: String,
    required: true,
    default: 'email@gmail.com'
  },
  username: {
    type: String,
    required: true,
    default: 'username'
  },
  password: {
    type: String,
    required: true,
    default: 'username'
  }
  // dateOfEntry: {
  //   type: Date,
  //   required: true,
  //   default: Date.now()
  // }
})

module.exports = Item = mongoose.model('user', userSchema)