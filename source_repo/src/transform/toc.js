'use strict';

/**
 * Generate a Markdown-formatted table of contents from extracted headings.
 *
 * Output format:
 *   - {text}         (for h2)
 *     - {text}       (for h3)
 *       - {text}     (for h4)
 *   ...
 *
 * h1 headings are treated as the document title and excluded from the TOC.
 * Indentation is 2 spaces per level below h2.
 * Each entry links to its anchor slug.
 *
 * @param {Array<{level: number, text: string, slug: string}>} headings
 * @returns {string}
 */
function generateToc(headings) {
  if (!headings || headings.length === 0) {
    return '';
  }

  const tocLines = [];

  for (const heading of headings) {
    // Skip h1 (document title)
    if (heading.level === 1) {
      continue;
    }

    const indent = '  '.repeat(heading.level - 2);
    const line = `${indent}- [${heading.text}](#${heading.slug})`;
    tocLines.push(line);
  }

  return tocLines.join('\n');
}

module.exports = { generateToc };