#!/usr/bin/env node

'use strict';

const { createCli } = require('../src/cli');
const { MdForgeError } = require('../src/utils/errors');
const logger = require('../src/utils/logger');

async function main() {
  const cli = createCli();

  try {
    await cli.parseAsync(process.argv);
  } catch (err) {
    if (err instanceof MdForgeError) {
      logger.error(err.message);
      process.exit(err.exitCode);
    }
    logger.error(`Unexpected error: ${err.message}`);
    process.exit(1);
  }
}

main();