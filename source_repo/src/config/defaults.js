'use strict';

/**
 * Default configuration values for mdforge.
 */
const DEFAULTS = {
  // Maximum file size to process (in bytes)
  maxFileSize: 10 * 1024 * 1024, // 10MB

  // Supported file extensions
  markdownExtensions: ['.md', '.markdown', '.mdown', '.mkd'],

  // Default output format for stats
  statsFormat: 'json',

  // Timeout for batch operations (ms)
  batchTimeout: 30000,

  // Maximum recursion depth for directory scanning
  maxDepth: 10,

  // Whether to follow symlinks
  followSymlinks: false,

  // Default encoding
  encoding: 'utf-8',

  // HTML conversion options
  html: {
    wrapInBody: false,
    includeDoctype: false,
    escapeHtml: true,
  },

  // TOC generation options
  toc: {
    minLevel: 2,
    maxLevel: 4,
    ordered: false,
  },
};

/**
 * Merge user config with defaults (shallow).
 * @param {object} userConfig
 * @returns {object}
 */
function mergeConfig(userConfig = {}) {
  return { ...DEFAULTS, ...userConfig };
}

module.exports = { DEFAULTS, mergeConfig };