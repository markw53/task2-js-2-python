'use strict';

const chalk = require('chalk');

/**
 * Simple logging utility with colored output.
 */
const logger = {
  /**
   * Log an informational message.
   * @param {string} msg
   */
  info(msg) {
    console.error(chalk.blue('[INFO]') + ' ' + msg);
  },

  /**
   * Log a success message.
   * @param {string} msg
   */
  success(msg) {
    console.error(chalk.green('[OK]') + ' ' + msg);
  },

  /**
   * Log a warning message.
   * @param {string} msg
   */
  warn(msg) {
    console.error(chalk.yellow('[WARN]') + ' ' + msg);
  },

  /**
   * Log an error message.
   * @param {string} msg
   */
  error(msg) {
    console.error(chalk.red('[ERROR]') + ' ' + msg);
  },

  /**
   * Log a debug message (only if MDFORGE_DEBUG is set).
   * @param {string} msg
   */
  debug(msg) {
    if (process.env.MDFORGE_DEBUG) {
      console.error(chalk.gray('[DEBUG]') + ' ' + msg);
    }
  },
};

module.exports = logger;