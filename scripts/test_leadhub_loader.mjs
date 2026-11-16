import test from "node:test";
import assert from "node:assert/strict";
import { initializeLeadHub, safeLeadHubOrigin } from "../site/leadhub-loader.mjs";

test("accepts only an HTTPS LeadHub origin", () => {
  assert.equal(safeLeadHubOrigin("https://leads.example.org"), "https://leads.example.org");
  for (const value of ["", "http://leads.example.org", "javascript:alert(1)", "https://user:pass@leads.example.org", "https://leads.example.org/path", "https://leads.example.org/?token=x"]) {
    assert.equal(safeLeadHubOrigin(value), "", value);
  }
});

test("loads the signup widget only for a valid configured origin", () => {
  const panel = { hidden: true };
  const appended = [];
  const doc = {
    querySelector: () => panel,
    createElement: () => ({}),
    head: { append: (script) => appended.push(script) },
  };
  assert.equal(initializeLeadHub(doc, "http://leads.example.org"), false);
  assert.equal(appended.length, 0);
  assert.equal(initializeLeadHub(doc, "https://leads.example.org"), true);
  assert.equal(appended[0].src, "https://leads.example.org/embed.js");
  assert.equal(panel.hidden, true);
  appended[0].onload();
  assert.equal(panel.hidden, false);
  appended[0].onerror();
  assert.equal(panel.hidden, true);
});
