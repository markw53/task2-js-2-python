'use strict';

const { Command } = require('commander');
const path = require('path');
const mdforge = require('./index');
const logger = require('./utils/logger');
const { MdForgeError } = require('./utils/errors');

function createCli() {
  const program = new Command();

  program
    .name('mdforge')
    .description('A CLI toolkit for parsing, validating, and transforming Markdown files')
    .version('1.2.0');

  program
    .command('parse <file>')
    .description('Parse a Markdown file and display its metadata')
    .action(async (file) => {
      const filePath = path.resolve(file);
      const result = await mdforge.parseFile(filePath);
      const output = {
        file: filePath,
        frontmatter: result.frontmatter,
        headings: result.headings,
        links: result.links,
        codeBlocks: result.codeBlocks,
        wordCount: result.wordCount,
      };
      console.log(JSON.stringify(output, null, 2));
    });

  program
    .command('toc <file>')
    .description('Generate a table of contents')
    .action(async (file) => {
      const filePath = path.resolve(file);
      const toc = await mdforge.generateToc(filePath);
      console.log(toc);
    });

  program
    .command('html <file>')
    .description('Convert Markdown to simplified HTML')
    .action(async (file) => {
      const filePath = path.resolve(file);
      const html = await mdforge.convertToHtml(filePath);
      console.log(html);
    });

  program
    .command('stats <path>')
    .description('Compute statistics for a file or directory')
    .action(async (targetPath) => {
      const resolved = path.resolve(targetPath);
      const stats = await mdforge.computeStats(resolved);
      console.log(JSON.stringify(stats, null, 2));
    });

  program
    .command('validate <dir>')
    .description('Validate internal links across a directory')
    .action(async (dir) => {
      const dirPath = path.resolve(dir);
      const result = await mdforge.validateLinks(dirPath);

      if (result.valid) {
        logger.success('All internal links are valid.');
        console.log(JSON.stringify(result, null, 2));
      } else {
        logger.warn(`Found ${result.brokenLinks.length} broken link(s).`);
        console.log(JSON.stringify(result, null, 2));
        throw new MdForgeError(
          `Validation failed: ${result.brokenLinks.length} broken link(s)`,
          2
        );
      }
    });

  program
    .command('batch <dir>')
    .description('Batch process a directory of Markdown files')
    .requiredOption('-o, --output <outdir>', 'Output directory for JSON files')
    .action(async (dir, opts) => {
      const inputDir = path.resolve(dir);
      const outputDir = path.resolve(opts.output);

      const fs = require('fs').promises;
      await fs.mkdir(outputDir, { recursive: true });

      const result = await mdforge.batchProcess(inputDir, outputDir);
      console.log(JSON.stringify(result, null, 2));

      if (result.failed > 0) {
        logger.warn(`${result.failed} file(s) failed processing.`);
      }
      logger.success(`Batch complete: ${result.processed} processed, ${result.failed} failed.`);
    });

  return program;
}

module.exports = { createCli };