'use strict';

/**
 * Compute the word count of Markdown body content.
 * Strips code blocks and counts whitespace-delimited tokens.
 *
 * @param {string} body
 * @returns {number}
 */
function computeWordCount(body) {
  // Remove fenced code blocks
  const stripped = body.replace(/(`{3,}|~{3,})[\s\S]*?\1/g, '');

  // Remove inline code
  const noInlineCode = stripped.replace(/`[^`]+`/g, '');

  // Remove Markdown syntax characters but keep words
  const cleaned = noInlineCode
    .replace(/[#*_$$$$()>|~`-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

  if (cleaned.length === 0) {
    return 0;
  }

  return cleaned.split(/\s+/).length;
}

/**
 * Build a structured metadata object from parsed components.
 *
 * @param {object} components
 * @returns {object}
 */
function buildMetadata(components) {
  const {
    filePath,
    frontmatter,
    headings,
    links,
    codeBlocks,
    wordCount,
    rawContent,
    bodyContent,
  } = components;

  const title = _inferTitle(frontmatter, headings);

  return {
    filePath,
    title,
    frontmatter,
    headings,
    links,
    codeBlocks,
    wordCount,
    lineCount: rawContent.split('\n').length,
    hasfrontmatter: Object.keys(frontmatter).length > 0,
    headingCount: headings.length,
    linkCount: links.length,
    codeBlockCount: codeBlocks.length,
    internalLinks: links.filter((l) => l.type === 'internal'),
    externalLinks: links.filter((l) => l.type === 'external'),
    anchorLinks: links.filter((l) => l.type === 'anchor'),
  };
}

/**
 * Infer the document title from frontmatter or the first h1 heading.
 * @param {object} frontmatter
 * @param {Array} headings
 * @returns {string|null}
 * @private
 */
function _inferTitle(frontmatter, headings) {
  if (frontmatter.title) {
    return String(frontmatter.title);
  }

  const h1 = headings.find((h) => h.level === 1);
  if (h1) {
    return h1.text;
  }

  return null;
}

module.exports = { computeWordCount, buildMetadata };