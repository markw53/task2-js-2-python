#!/bin/bash
set -e

cd /target
npm install
npx jest --forceExit --detectOpenHandles --verbose 2>&1

#!/bin/bash
set -e

cd /target
pip install -e .
MDFORGE_BIN='python3 -m mdforge' python3 -m pytest /target/tests/test_mdforge_behavioral.py \
    --rootdir=/target/tests \
    -v \
    --tb=short \
    --no-header \
    -rA \
    --color=no \
    -p no:cacheprovider 2>&1