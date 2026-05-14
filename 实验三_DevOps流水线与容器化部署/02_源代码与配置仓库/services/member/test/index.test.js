const test = require("node:test");
const assert = require("node:assert/strict");
const { memberProfile, normalizeConsent } = require("../src/index.js");

test("member profile masks phone", () => {
  const profile = memberProfile();
  assert.equal(profile.id, "m_1001");
  assert.match(profile.phoneMasked, /\*\*\*\*/);
});

test("consent normalization", () => {
  const consent = normalizeConsent({ type: "MARKETING", granted: false });
  assert.equal(consent.type, "MARKETING");
  assert.equal(consent.granted, false);
});
