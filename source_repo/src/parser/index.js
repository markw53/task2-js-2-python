'use strict';

const { parseFrontmatter } = require('./frontmatter');
const { extractHeadings } = require('./headings');
const { extractLinks } = require('./links');
const { extractCodeBlocks } = require('./codeblocks');
const { computeWordCount, buildMetadata } = require('./metadata');

/**
 * Parse a Markdown string and extract all structured metadata.
 * @param {string} content - Raw Markdown content
 * @param {string} filePath - Path to the source file (for error reporting)
 * @returns {object} Parsed metadata object
 */
function parse(content, filePath) {
  if (typeof content !== 'string') {
    throw new TypeError(`Expected string content for ${filePath}, got ${typeof content}`);
  }

  const frontmatter = parseFrontmatter(content);
  const body = frontmatter._body;

  const headings = extractHeadings(body);
  const links = extractLinks(body);
  const codeBlocks = extractCodeBlocks(body);
  const wordCount = computeWordCount(body);

  return buildMetadata({
    filePath,
    frontmatter: frontmatter.data,
    headings,
    links,
    codeBlocks,
    wordCount,
    rawContent: content,
    bodyContent: body,
  });
}

module.exports = { parse };