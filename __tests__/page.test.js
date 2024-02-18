const request = require("supertest");
const app = require("../app");
const mongoose = require("mongoose");
require("dotenv").config();

const mysql = require('mysql2');

beforeAll(async () => {
   await mysql.createConnection({
    connectionLimit: 10,
    host: process.env.mysqlhost,
    port: 3306,
    user: process.env.mysqlUser,
    password: process.env.mysqlPassword,
    database: process.env.mysqlDB 
  });
});

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

// describe("GET viewDataPage", () => {
//   it("returns status code 200 if the view data page loaded", async () => {
//     const res = await request(app).get("/view-data");
//     expect(res.statusCode).toEqual(200);
//   });
// });

// describe("GET invitePage", () => {
//   it("returns status code 200 if the invite page loaded", async () => {
//     const res = await request(app).get("/invite");
//     expect(res.statusCode).toEqual(200);
//   });
// });

// describe("GET Table", () => {
//   it("returns status code 200 when the user is logged in", async () => {
//     const res = await request(app).post("/table").send({req.session.logged_in = true});
//     expect(res.statusCode).toEqual(200);
//   });
// });