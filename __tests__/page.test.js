const request = require("supertest");
const app = require("../app");
const mongoose = require("mongoose");
require("dotenv").config();

beforeAll(async () => {
   await mongoose.connect(process.env.DATABASE_URL);
});

afterAll(async () => {
  // Closing the DB connection allows Jest to exit successfully.
  await mongoose.connection.close();
});


// describe("GET Home", () => {
//   it("returns status code 200 if the home page loaded", async () => {
//     const res = await request(app).get("/");
//     expect(res.statusCode).toEqual(200);
//   });
// });

// describe("GET Map", () => {
//   it("returns status code 200 if the map page loaded", async () => {
//     const res = await request(app).get("/map");
//     expect(res.statusCode).toEqual(200);
//   });
// });

describe("GET loginPage", () => {
  it("returns status code 200 if the researcher login page loaded", async () => {
    const res = await request(app).get("/rlogin");
    expect(res.statusCode).toEqual(200);
  });
});

// describe("GET Table", () => {
//   it("returns status code 200 when the user is logged in", async () => {
//     const res = await request(app).post("/table").send({session.logged_in});
//     expect(res.statusCode).toEqual(200);
//   });
// });