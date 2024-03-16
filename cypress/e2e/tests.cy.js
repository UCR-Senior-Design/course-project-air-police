describe("home page", () => {
  it("home page participation button works", () => {
    cy.visit("localhost:3000");
    cy.get(".nav-link").click();
    cy.get(".navbar-text").should("be.hidden");
    cy.get(":nth-child(3) > .dropdown-item").should("not.exist");
    cy.get(":nth-child(4) > .dropdown-item").should("not.exist");
    cy.get(":nth-child(1) > .dropdown-item").should("exist");
    cy.get(":nth-child(1) > .dropdown-item").click();
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/login");
    });
  });

  it(" researcher login button works", () => {
    cy.visit("localhost:3000");
    cy.get(".nav-link").click();
    cy.get(":nth-child(2) > .dropdown-item").should("exist");
    cy.get(":nth-child(2) > .dropdown-item").click();
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/rlogin");
    });
  });

  it(" researcher login should work if user exists", () => {
    cy.visit("localhost:3000");
    cy.get(".nav-link").click();
    cy.get(":nth-child(2) > .dropdown-item").should("exist");
    cy.get(":nth-child(2) > .dropdown-item").click();
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/rlogin");
    });
    cy.get("#username").type("pyTest");
    cy.get("#password").type("1234");
    cy.get("#submit").click();
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/table");
    });
  });
});
describe("visually", () => {
  it("passes", () => {
    cy.visit("localhost:3000");
  });
});
