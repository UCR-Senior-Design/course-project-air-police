const app = require("../app");
const request = require("supertest");



describe("GET Home", () => {
    it("should confirm the home page loaded", async () => {
      const res = await request(app).get("/");
      expect(res.statusCode).toBe(200);
    });
  });