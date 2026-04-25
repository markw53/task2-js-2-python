'use strict';

const fs = require('fs').promises;
const path = require('path');
const { glob } = require('glob');
const { MdForgeError } = require('./errors');

/**
 * Read a file and return its content as a UTF-8 string.
 * @param {string} filePath
 * @returns {Promise<string>}
 */
async function readFile(filePath) {
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    return content;
  } catch (err) {
    if (err.code === 'ENOENT') {
      throw new MdForgeError(`File not found: ${filePath}`, 1);
    }
    throw new MdForgeError(`Error reading file ${filePath}: ${err.message}`, 1);
  }
}

/**
 * Read all Markdown files from a directory (recursive).
 * Returns an array of absolute file paths.
 * @param {string} dirPath
 * @returns {Promise<string[]>}
 */
async function readDirectory(dirPath) {
  try {
    const stat = await fs.stat(dirPath);
    if (!stat.isDirectory()) {
      throw new MdForgeError(`Not a directory: ${dirPath}`, 1);
    }
  } catch (err) {
    if (err instanceof MdForgeError) throw err;
    throw new MdForgeError(`Cannot access directory: ${dirPath}`, 1);
  }

  const pattern = path.join(dirPath, '**/*.md');
  const files = await glob(pattern, { nodir: true, absolute: true });

  if (files.length === 0) {
    throw new MdForgeError(`No Markdown files found in: ${dirPath}`, 1);
  }

  // Sort for deterministic output
  return files.sort();
}

/**
 * Write content to a file, creating parent directories as needed.
 * @param {string} filePath
 * @param {string} content
 * @returns {Promise<void>}
 */
async function writeFile(filePath, content) {
  try {
    const dir = path.dirname(filePath);
    await fs.mkdir(dir, { recursive: true });
    await fs.writeFile(filePath, content, 'utf-8');
  } catch (err) {
    throw new MdForgeError(`Error writing file ${filePath}: ${err.message}`, 1);
  }
}

module.exports = { readFile, readDirectory, writeFile };