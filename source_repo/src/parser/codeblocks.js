'use strict';

/**
 * Extract fenced code blocks from Markdown body content.
 *
 * Supports both backtick (```) and tilde (~~~) fencing.
 *
 * Each code block includes:
 *  - language: the language identifier (empty string if none)
 *  - code: the code content (without fences)
 *  - startLine: 1-based line number of the opening fence
 *  - endLine: 1-based line number of the closing fence
 *
 * @param {string} body
 * @returns {Array<{language: string, code: string, startLine: number, endLine: number}>}
 */
function extractCodeBlocks(body) {
  const blocks = [];
  const lines = body.split('\n');
  let currentBlock = null;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trimStart();

    if (currentBlock === null) {
      // Check for opening fence
      const openMatch = trimmed.match(/^(`{3,}|~{3,})(\S*)$/);
      if (openMatch) {
        currentBlock = {
          fence: openMatch[1][0],          // '`' or '~'
          fenceLen: openMatch[1].length,
          language: openMatch[2] || '',
          codeLines: [],
          startLine: i + 1,
        };
      }
    } else {
      // Check for closing fence (must match same char and at least same length)
      const closePattern = new RegExp(
        `^\\${currentBlock.fence}{${currentBlock.fenceLen},}\\s*$`
      );

      if (closePattern.test(trimmed)) {
        blocks.push({
          language: currentBlock.language,
          code: currentBlock.codeLines.join('\n'),
          startLine: currentBlock.startLine,
          endLine: i + 1,
        });
        currentBlock = null;
      } else {
        currentBlock.codeLines.push(line);
      }
    }
  }

  // Unclosed code blocks are discarded (match common Markdown parser behavior)
  return blocks;
}

module.exports = { extractCodeBlocks };