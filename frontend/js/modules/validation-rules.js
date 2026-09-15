/**
 * VidhiMeet Validation Rules ES Module
 * Re-exports ValidationRules for ES module environments.
 */
import "../validation-rules.js";

export const ValidationRules = (typeof window !== "undefined" && window.ValidationRules)
  ? window.ValidationRules
  : (typeof globalThis !== "undefined" ? globalThis.ValidationRules : {});

export default ValidationRules;
