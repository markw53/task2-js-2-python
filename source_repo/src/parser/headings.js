'use strict';

/**
 * Extract all Markdown headings from the body content.
 * Supports ATX-style headings (# through ######).
 *
 * Each heading includes:
 *  - level (1–6)
 *  - text (trimmed heading text)
 *  - slug (URL-friendly anchor)
 *  - line (1-based line number)
 *
 * @param {string} body
 * @returns {Array<{level: number, text: string, slug: string, line: number}>}
 */
function extractHeadings(body) {
  const headings = [];
  const lines = body.split('\n');
  let inCodeBlock = false;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Track fenced code blocks to avoid false positives
    if (line.trimStart().startsWith('```') || line.trimStart().startsWith('~~~')) {
      inCodeBlock = !inCodeBlock;
      continue;
    }

    if (inCodeBlock) {
      continue;
    }

    const match = line.match(/^(#{1,6})\s+(.+)$/);
    if (match) {
      const level = match[1].length;
      const text = match[2].trim();
      const slug = generateSlug(text);

      headings.push({
        level,
        text,
        slug,
        line: i + 1,
      });
    }
  }

  return headings;
}

/**
 * Generate a URL-friendly slug from heading text.
 * Lowercases, replaces spaces with hyphens, removes non-alphanumeric chars
 * (except hyphens), and collapses multiple hyphens.
 *
 * @param {string} text
 * @returns {string}
 */
function generateSlug(text) {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

module.exports = { extractHeadings, generateSlug };