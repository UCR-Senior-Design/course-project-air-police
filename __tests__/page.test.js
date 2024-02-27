const request = require("supertest");
const app = require("../app");
const mongoose = require("mongoose");
require("dotenv").config();

// const mysql = require('mysql2');

// beforeAll(async () => {
//    await mysql.createConnection({
//     connectionLimit: 10,
//     host: process.env.mysqlhost,
//     port: 3306,
//     user: process.env.mysqlUser,
//     password: process.env.mysqlPassword,
//     database: process.env.mysqlDB 
//   });
// });

// afterAll(async () => {
//   // Closing the DB connection allows Jest to exit successfully.
//   await mysql.close();
// });

describe("GET Home", () => {
  it("returns status code 200 if the home page loaded", async () => {
    const res = await request(app).get("/");
    expect(res.statusCode).toEqual(200);
  });
});

describe("GET Map", () => {
  it("returns status code 200 if the map page loaded", async () => {
    const res = await request(app).get("/map");
    expect(res.statusCode).toEqual(200);
  });
});

describe("GET loginPage", () => {
  it("returns status code 200 if the researcher login page loaded", async () => {
    const res = await request(app).get("/rlogin");
    expect(res.statusCode).toEqual(200);
  });
});

describe("GET registerPage", () => {
  it("returns status code 200 if the researcher registration page loaded", async () => {
    const res = await request(app).get("/register");
    expect(res.statusCode).toEqual(200);
  });
});

// describe("GET data-analysis-testing", () => {
//   it("returns status code 200 if the view data page loaded", async () => {
//     const res = await request(app).get("/data-analysis-testing");
//     expect(res.statusCode).toEqual(200);
//   });
// });

describe("GET invitePage", () => {
  it("returns status code 302 if the invite page redirects with no token", async () => {
    const res = await request(app).get("/invite");
    expect(res.statusCode).toEqual(302);
  });
});

describe("GET Table", () => {
  it("returns status code 302 (redirect) when the user is not logged in", async () => {
    const res  = await request(app).get("/table");
    expect(res.statusCode).toEqual(302);
  });
});

// describe("GET Table", () => {
//   it("returns status code 200 when the user is logged in", async () => {
//     const res  = await request(app).get("/table");
//     //response.send({session.logged_in : true});
//     expect(res.statusCode).toEqual(200);
//   });
// });

// describe("GET Table", () => {
//   it("returns status code 200 when the user is logged in", async () => {
//     const res  = await request(app).get("/table");
//     //response.send({session.logged_in : true});
//     expect(res.statusCode).toEqual(302);
//   });
// });
// // req.session.logged_in = true