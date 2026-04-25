'use strict';

const path = require('path');

/**
 * Validate all internal links across a corpus of parsed Markdown files.
 *
 * Internal links are expected to point to:
 *  - Other files in the corpus (e.g., ./other.md)
 *  - Anchors within files (e.g., ./other.md#section or #section)
 *
 * @param {object} corpus - Map of filePath → parsed metadata
 * @returns {object} Validation result
 */
function validateCorpus(corpus) {
  const filePaths = Object.keys(corpus);
  const brokenLinks = [];
  const validLinks = [];
  const checkedCount = { internal: 0, anchor: 0 };

  // Build a set of known files (normalized)
  const knownFiles = new Set();
  for (const fp of filePaths) {
    knownFiles.add(path.resolve(fp));
  }

  // Build a map of file → known anchors (heading slugs)
  const anchorMap = {};
  for (const [fp, parsed] of Object.entries(corpus)) {
    const resolved = path.resolve(fp);
    anchorMap[resolved] = new Set(
      parsed.headings.map((h) => h.slug)
    );
  }

  for (const [fp, parsed] of Object.entries(corpus)) {
    const fileDir = path.dirname(path.resolve(fp));

    for (const link of parsed.links) {
      if (link.type === 'internal') {
        checkedCount.internal += 1;
        const result = _validateInternalLink(link, fp, fileDir, knownFiles, anchorMap);
        if (result.valid) {
          validLinks.push(result);
        } else {
          brokenLinks.push(result);
        }
      } else if (link.type === 'anchor') {
        checkedCount.anchor += 1;
        const result = _validateAnchorLink(link, fp, anchorMap);
        if (result.valid) {
          validLinks.push(result);
        } else {
          brokenLinks.push(result);
        }
      }
      // External and "other" links are not validated
    }
  }

  return {
    valid: brokenLinks.length === 0,
    totalChecked: checkedCount.internal + checkedCount.anchor,
    validCount: validLinks.length,
    brokenCount: brokenLinks.length,
    brokenLinks,
    checkedCount,
  };
}

/**
 * Validate an internal link (relative path to another file, optionally with anchor).
 * @private
 */
function _validateInternalLink(link, sourceFile, fileDir, knownFiles, anchorMap) {
  const urlParts = link.url.split('#');
  const filePart = urlParts[0];
  const anchorPart = urlParts[1] || null;

  const targetPath = path.resolve(fileDir, filePart);

  const result = {
    source: sourceFile,
    line: link.line,
    text: link.text,
    url: link.url,
    type: 'internal',
    valid: true,
    reason: null,
  };

  if (!knownFiles.has(targetPath)) {
    result.valid = false;
    result.reason = `File not found: ${filePart}`;
    return result;
  }

  if (anchorPart) {
    const targetAnchors = anchorMap[targetPath];
    if (!targetAnchors || !targetAnchors.has(anchorPart)) {
      result.valid = false;
      result.reason = `Anchor not found: #${anchorPart} in ${filePart}`;
      return result;
    }
  }

  return result;
}

/**
 * Validate an anchor link (same-page reference like #section).
 * @private
 */
function _validateAnchorLink(link, sourceFile, anchorMap) {
  const anchor = link.url.slice(1); // Remove leading #
  const resolvedSource = path.resolve(sourceFile);

  const result = {
    source: sourceFile,
    line: link.line,
    text: link.text,
    url: link.url,
    type: 'anchor',
    valid: true,
    reason: null,
  };

  const sourceAnchors = anchorMap[resolvedSource];
  if (!sourceAnchors || !sourceAnchors.has(anchor)) {
    result.valid = false;
    result.reason = `Anchor not found: ${link.url} in current document`;
    return result;
  }

  return result;
}

module.exports = { validateCorpus };