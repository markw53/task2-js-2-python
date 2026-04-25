'use strict';

/**
 * Convert Markdown content to simplified HTML.
 *
 * This is a lightweight converter that handles:
 *  - Headings (# through ######) → <h1> through <h6>
 *  - Bold (**text** or __text__) → <strong>
 *  - Italic (*text* or _text_) → <em>
 *  - Inline code (`code`) → <code>
 *  - Fenced code blocks → <pre><code>
 *  - Links [text](url) → <a href="url">
 *  - Unordered lists (- or *) → <ul><li>
 *  - Ordered lists (1. 2.) → <ol><li>
 *  - Paragraphs → <p>
 *  - Horizontal rules (--- or ***) → <hr>
 *  - Blockquotes (>) → <blockquote>
 *
 * It does NOT handle:
 *  - Tables
 *  - Images (treated as links)
 *  - Nested lists beyond one level
 *  - Reference-style links
 *
 * @param {string} content - Raw Markdown (may include frontmatter)
 * @returns {string} Simplified HTML
 */
function toHtml(content) {
  // Strip frontmatter if present
  const body = _stripFrontmatter(content);
  const lines = body.split('\n');
  const htmlParts = [];

  let inCodeBlock = false;
  let codeBlockLang = '';
  let codeLines = [];
  let inList = false;
  let listType = null;
  let inBlockquote = false;
  let paragraphLines = [];

  function flushParagraph() {
    if (paragraphLines.length > 0) {
      const text = paragraphLines.join(' ');
      const inlined = _inlineMarkdown(text);
      htmlParts.push(`<p>${inlined}</p>`);
      paragraphLines = [];
    }
  }

  function flushList() {
    if (inList) {
      htmlParts.push(listType === 'ul' ? '</ul>' : '</ol>');
      inList = false;
      listType = null;
    }
  }

  function flushBlockquote() {
    if (inBlockquote) {
      htmlParts.push('</blockquote>');
      inBlockquote = false;
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    // Fenced code blocks
    if (trimmed.startsWith('```') || trimmed.startsWith('~~~')) {
      if (!inCodeBlock) {
        flushParagraph();
        flushList();
        flushBlockquote();
        inCodeBlock = true;
        codeBlockLang = trimmed.replace(/^[`~]+/, '').trim();
        codeLines = [];
        continue;
      } else {
        const langAttr = codeBlockLang ? ` class="language-${codeBlockLang}"` : '';
        const codeContent = _escapeHtml(codeLines.join('\n'));
        htmlParts.push(`<pre><code${langAttr}>${codeContent}</code></pre>`);
        inCodeBlock = false;
        codeBlockLang = '';
        codeLines = [];
        continue;
      }
    }

    if (inCodeBlock) {
      codeLines.push(line);
      continue;
    }

    // Horizontal rule
    if (/^(-{3,}|\*{3,}|_{3,})$/.test(trimmed)) {
      flushParagraph();
      flushList();
      flushBlockquote();
      htmlParts.push('<hr>');
      continue;
    }

    // Headings
    const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
      flushParagraph();
      flushList();
      flushBlockquote();
      const level = headingMatch[1].length;
      const text = _inlineMarkdown(headingMatch[2].trim());
      htmlParts.push(`<h${level}>${text}</h${level}>`);
      continue;
    }

    // Blockquote
    if (trimmed.startsWith('>')) {
      flushParagraph();
      flushList();
      if (!inBlockquote) {
        htmlParts.push('<blockquote>');
        inBlockquote = true;
      }
      const quoteText = _inlineMarkdown(trimmed.replace(/^>\s?/, ''));
      htmlParts.push(`<p>${quoteText}</p>`);
      continue;
    } else if (inBlockquote) {
      flushBlockquote();
    }

    // Unordered list
    const ulMatch = trimmed.match(/^[-*]\s+(.+)$/);
    if (ulMatch) {
      flushParagraph();
      flushBlockquote();
      if (!inList || listType !== 'ul') {
        flushList();
        htmlParts.push('<ul>');
        inList = true;
        listType = 'ul';
      }
      htmlParts.push(`<li>${_inlineMarkdown(ulMatch[1])}</li>`);
      continue;
    }

    // Ordered list
    const olMatch = trimmed.match(/^\d+\.\s+(.+)$/);
    if (olMatch) {
      flushParagraph();
      flushBlockquote();
      if (!inList || listType !== 'ol') {
        flushList();
        htmlParts.push('<ol>');
        inList = true;
        listType = 'ol';
      }
      htmlParts.push(`<li>${_inlineMarkdown(olMatch[1])}</li>`);
      continue;
    }

    // If we were in a list and hit a non-list line, close it
    if (inList && trimmed.length > 0) {
      flushList();
    }

    // Empty line: flush paragraph
    if (trimmed.length === 0) {
      flushParagraph();
      continue;
    }

    // Paragraph text
    paragraphLines.push(trimmed);
  }

  // Flush remaining state
  flushParagraph();
  flushList();
  flushBlockquote();

  if (inCodeBlock) {
    // Unclosed code block — emit what we have
    const codeContent = _escapeHtml(codeLines.join('\n'));
    htmlParts.push(`<pre><code>${codeContent}</code></pre>`);
  }

  return htmlParts.join('\n');
}

/**
 * Apply inline Markdown transformations.
 * @param {string} text
 * @returns {string}
 * @private
 */
function _inlineMarkdown(text) {
  let result = text;

  // Inline code (must be done before other transforms to protect code content)
  result = result.replace(/`([^`]+)`/g, (_, code) => {
    return `<code>${_escapeHtml(code)}</code>`;
  });

  // Bold (**text** or __text__)
  result = result.replace(/\*\*(.+?)\*\*/g, '<strong>\$1</strong>');
  result = result.replace(/__(.+?)__/g, '<strong>\$1</strong>');

  // Italic (*text* or _text_) — must come after bold
  result = result.replace(/\*(.+?)\*/g, '<em>\$1</em>');
  result = result.replace(/_(.+?)_/g, '<em>\$1</em>');

  // Links [text](url)
  result = result.replace(/$$([^$$]+)\]\(([^)]+)\)/g, '<a href="\$2">\$1</a>');

  return result;
}

/**
 * Escape HTML special characters.
 * @param {string} text
 * @returns {string}
 * @private
 */
function _escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/**
 * Strip YAML frontmatter from content.
 * @param {string} content
 * @returns {string}
 * @private
 */
function _stripFrontmatter(content) {
  const match = content.match(/^---\n[\s\S]*?\n---\n?/);
  if (match) {
    return content.slice(match[0].length);
  }
  return content;
}

module.exports = { toHtml };