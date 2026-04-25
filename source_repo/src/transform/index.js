'use strict';

const { generateToc } = require('./toc');
const { toHtml } = require('./html');
const { computeStats, aggregateStats } = require('./stats');

module.exports = {
  generateToc,
  toHtml,
  computeStats,
  aggregateStats,
};