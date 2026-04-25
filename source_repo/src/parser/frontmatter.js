'use strict';

const matter = require('gray-matter');

/**
 * Parse YAML frontmatter from Markdown content.
 * Returns an object with `data` (parsed YAML) and `_body` (content without frontmatter).
 *
 * If no frontmatter is present, returns empty data and full content as body.
 *
 * @param {string} content
 * @returns {{ data: object, _body: string }}
 */
function parseFrontmatter(content) {
  try {
    const result = matter(content);
    return {
      data: result.data || {},
      _body: result.content || '',
    };
  } catch (err) {
    // If frontmatter parsing fails (malformed YAML), treat entire content as body
    return {
      data: {},
      _body: content,
    };
  }
}

module.exports = { parseFrontmatter };