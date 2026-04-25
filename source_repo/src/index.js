'use strict';

const parser = require('./parser');
const transform = require('./transform');
const validator = require('./validator');
const { readFile, readDirectory, writeFile } = require('./utils/fileio');
const { MdForgeError } = require('./utils/errors');

/**
 * Parse a single Markdown file and return its full metadata.
 * @param {string} filePath
 * @returns {Promise<object>}
 */
async function parseFile(filePath) {
  const content = await readFile(filePath);
  return parser.parse(content, filePath);
}

/**
 * Generate a table of contents for a single file.
 * @param {string} filePath
 * @returns {Promise<string>}
 */
async function generateToc(filePath) {
  const content = await readFile(filePath);
  const parsed = parser.parse(content, filePath);
  return transform.generateToc(parsed.headings);
}

/**
 * Convert a Markdown file to simplified HTML.
 * @param {string} filePath
 * @returns {Promise<string>}
 */
async function convertToHtml(filePath) {
  const content = await readFile(filePath);
  return transform.toHtml(content);
}

/**
 * Compute statistics for a file or directory.
 * @param {string} targetPath
 * @returns {Promise<object>}
 */
async function computeStats(targetPath) {
  const files = await _resolveFiles(targetPath);
  const allStats = [];

  for (const fp of files) {
    const content = await readFile(fp);
    const parsed = parser.parse(content, fp);
    allStats.push(transform.computeStats(parsed, fp));
  }

  return transform.aggregateStats(allStats);
}

/**
 * Validate internal links across a directory of Markdown files.
 * @param {string} dirPath
 * @returns {Promise<object>}
 */
async function validateLinks(dirPath) {
  const files = await readDirectory(dirPath);
  const corpus = {};

  for (const fp of files) {
    const content = await readFile(fp);
    corpus[fp] = parser.parse(content, fp);
  }

  return validator.validateCorpus(corpus);
}

/**
 * Batch process a directory: parse all files and write JSON metadata
 * to an output directory.
 * @param {string} inputDir
 * @param {string} outputDir
 * @returns {Promise<object>}
 */
async function batchProcess(inputDir, outputDir) {
  const files = await readDirectory(inputDir);
  const results = { processed: 0, failed: 0, errors: [] };

  for (const fp of files) {
    try {
      const content = await readFile(fp);
      const parsed = parser.parse(content, fp);
      const stats = transform.computeStats(parsed, fp);
      const toc = transform.generateToc(parsed.headings);

      const output = {
        file: fp,
        metadata: parsed.frontmatter,
        headings: parsed.headings,
        links: parsed.links,
        codeBlocks: parsed.codeBlocks,
        stats: stats,
        toc: toc,
      };

      const path = require('path');
      const outName = path.basename(fp, '.md') + '.json';
      const outPath = path.join(outputDir, outName);
      await writeFile(outPath, JSON.stringify(output, null, 2));
      results.processed += 1;
    } catch (err) {
      results.failed += 1;
      results.errors.push({ file: fp, error: err.message });
    }
  }

  return results;
}

/**
 * Resolve a path to a list of Markdown files.
 * @param {string} targetPath
 * @returns {Promise<string[]>}
 * @private
 */
async function _resolveFiles(targetPath) {
  const fs = require('fs').promises;
  const stat = await fs.stat(targetPath);

  if (stat.isDirectory()) {
    return readDirectory(targetPath);
  }
  return [targetPath];
}

module.exports = {
  parseFile,
  generateToc,
  convertToHtml,
  computeStats,
  validateLinks,
  batchProcess,
};