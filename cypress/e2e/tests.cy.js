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
  
  it("correct id should redirect", () => {
    cy.visit("localhost:3000");
    cy.get(".nav-link").click();
    cy.get(".navbar-text").should("be.hidden");
    cy.get(":nth-child(3) > .dropdown-item").should("not.exist");
    cy.get(":nth-child(4) > .dropdown-item").should("not.exist");
    cy.get(":nth-child(1) > .dropdown-item").should("exist");
    cy.get(":nth-child(1) > .dropdown-item").click();
    cy.get("#monitorId").should("exist");
    cy.get("#monitorId").type("SSIF_G5_688");
    cy.get("#monitorId").type("{enter}");
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/success-page");
    });
    cy.get("#aqiChart").should("exist");
  });
  it("incorrect id should not redirect", () => {
    cy.visit("localhost:3000");
    cy.get(".nav-link").click();
    cy.get(".navbar-text").should("be.hidden");
    cy.get(":nth-child(3) > .dropdown-item").should("not.exist");
    cy.get(":nth-child(4) > .dropdown-item").should("not.exist");
    cy.get(":nth-child(1) > .dropdown-item").should("exist");
    cy.get(":nth-child(1) > .dropdown-item").click();
    cy.get("#monitorId").should("exist");
    cy.get("#monitorId").type("SSIF_2G_688");
    cy.get("#monitorId").type("{enter}");
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
  it(" researcher login should not redirect work if user does not exists", () => {
    cy.visit("localhost:3000");
    cy.get(".nav-link").click();
    cy.get(":nth-child(2) > .dropdown-item").should("exist");
    cy.get(":nth-child(2) > .dropdown-item").click();
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/rlogin");
    });
    cy.get("#username").type("dsnionoew");
    cy.get("#password").type("1234");
    cy.get("#submit").click();
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/rlogin");
    });
  });
  it("table contains 2 tables logout button should be visible ( and invite)", () => {
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
    cy.get(":nth-child(3) > .dropdown-item").should("exist");
    cy.get(":nth-child(4) > .dropdown-item").should("exist");
    cy.get("#errorTable").should("exist");
    cy.get("#normalTable").should("exist");
  });
  it("map should load and should change to pm10 when changed", () => {
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
    cy.get(".navbar-text").click();
    cy.location().should((loc) => {
      expect(loc.pathname.toString()).to.contain("/map");
    });
    cy.get("#pm_dropdown").should("exist");
  });
});
