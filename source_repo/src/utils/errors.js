'use strict';

/**
 * Custom error class for mdforge.
 * Carries an exit code for CLI error reporting.
 */
class MdForgeError extends Error {
  /**
   * @param {string} message
   * @param {number} [exitCode=1]
   */
  constructor(message, exitCode = 1) {
    super(message);
    this.name = 'MdForgeError';
    this.exitCode = exitCode;
  }
}

module.exports = { MdForgeError };