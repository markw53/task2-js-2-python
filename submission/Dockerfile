FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create venv and install target language dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir \
    pytest \
    click>=8.1.0 \
    python-frontmatter>=1.0.0

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

# Copy source JS repo
WORKDIR /source
COPY source_repo/ /source/

# Install JS dependencies and verify
RUN npm install
RUN node bin/mdforge.js --version

# --- MANDATORY: Zero-Test Environment ---
RUN rm -rf /source/tests/ /source/test/ /source/__tests__/ && \
    find /source -name "*.test.js" -delete && \
    find /source -name "*.spec.js" -delete && \
    find /source -name "test_*.js" -delete && \
    rm -f /source/prompt.txt /source/reasoning.txt

# --- ANTI-CHEATING: Squash history ---
RUN rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "source state - ready for translation" --quiet

# Initialize /target as empty git repo (required for test_patch.diff)
RUN mkdir -p /target && \
    cd /target && \
    git init

# --- MANDATORY: Create user with uid 1000 ---
RUN id user >/dev/null 2>&1 || useradd -m -u 1000 -s /bin/bash user
RUN chown -R user:user /source /target /opt/venv

USER user
WORKDIR /source