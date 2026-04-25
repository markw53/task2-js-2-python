'use strict';

/**
 * Compute statistics for a single parsed Markdown document.
 *
 * @param {object} parsed - Output from parser.parse()
 * @param {string} filePath - Path to the source file
 * @returns {object}
 */
function computeStats(parsed, filePath) {
  const languageDist = {};
  for (const block of parsed.codeBlocks) {
    const lang = block.language || 'unknown';
    languageDist[lang] = (languageDist[lang] || 0) + 1;
  }

  return {
    file: filePath,
    wordCount: parsed.wordCount,
    lineCount: parsed.lineCount,
    headingCount: parsed.headingCount,
    linkCount: parsed.linkCount,
    codeBlockCount: parsed.codeBlockCount,
    internalLinkCount: parsed.internalLinks.length,
    externalLinkCount: parsed.externalLinks.length,
    anchorLinkCount: parsed.anchorLinks.length,
    hasTitle: parsed.title !== null,
    hasFrontmatter: parsed.hasFrontmatter,
    codeLanguages: languageDist,
  };
}

/**
 * Aggregate statistics across multiple files.
 *
 * @param {Array<object>} statsArray - Array of per-file stats objects
 * @returns {object}
 */
function aggregateStats(statsArray) {
  if (statsArray.length === 0) {
    return {
      fileCount: 0,
      totalWordCount: 0,
      totalLineCount: 0,
      totalHeadings: 0,
      totalLinks: 0,
      totalCodeBlocks: 0,
      averageWordCount: 0,
      files: [],
      codeLanguages: {},
    };
  }

  let totalWords = 0;
  let totalLines = 0;
  let totalHeadings = 0;
  let totalLinks = 0;
  let totalCodeBlocks = 0;
  const codeLanguages = {};

  for (const s of statsArray) {
    totalWords += s.wordCount;
    totalLines += s.lineCount;
    totalHeadings += s.headingCount;
    totalLinks += s.linkCount;
    totalCodeBlocks += s.codeBlockCount;

    for (const [lang, count] of Object.entries(s.codeLanguages || {})) {
      codeLanguages[lang] = (codeLanguages[lang] || 0) + count;
    }
  }

  return {
    fileCount: statsArray.length,
    totalWordCount: totalWords,
    totalLineCount: totalLines,
    totalHeadings: totalHeadings,
    totalLinks: totalLinks,
    totalCodeBlocks: totalCodeBlocks,
    averageWordCount: Math.round(totalWords / statsArray.length),
    files: statsArray.map((s) => s.file),
    codeLanguages,
  };
}

module.exports = { computeStats, aggregateStats };