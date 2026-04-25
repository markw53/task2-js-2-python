'use strict';

/**
 * Extract all links from Markdown body content.
 *
 * Categorizes links as:
 *  - "internal": relative paths (e.g., ./other.md, ../docs/file.md, file.md#anchor)
 *  - "external": absolute URLs (http://, https://)
 *  - "anchor": same-page anchors (#section)
 *  - "other": mailto:, ftp://, etc.
 *
 * Each link includes:
 *  - text: the display text
 *  - url: the raw URL
 *  - type: one of the categories above
 *  - line: 1-based line number
 *
 * @param {string} body
 * @returns {Array<{text: string, url: string, type: string, line: number}>}
 */
function extractLinks(body) {
  const links = [];
  const lines = body.split('\n');
  let inCodeBlock = false;

  // Matches [text](url) — standard inline Markdown links
  const linkPattern = /$$([^$$]*)\]\(([^)]+)\)/g;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.trimStart().startsWith('```') || line.trimStart().startsWith('~~~')) {
      inCodeBlock = !inCodeBlock;
      continue;
    }

    if (inCodeBlock) {
      continue;
    }

    let match;
    linkPattern.lastIndex = 0;

    while ((match = linkPattern.exec(line)) !== null) {
      const text = match[1];
      const url = match[2].trim();
      const type = classifyLink(url);

      links.push({
        text,
        url,
        type,
        line: i + 1,
      });
    }
  }

  return links;
}

/**
 * Classify a URL into a link type.
 * @param {string} url
 * @returns {string}
 */
function classifyLink(url) {
  if (url.startsWith('#')) {
    return 'anchor';
  }
  if (url.startsWith('http://') || url.startsWith('https://')) {
    return 'external';
  }
  if (url.startsWith('mailto:') || url.startsWith('ftp://')) {
    return 'other';
  }
  return 'internal';
}

module.exports = { extractLinks, classifyLink };