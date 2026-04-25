FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    python3-pip \
    python3-venv \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y --no-install-recommends nodejs \
    && rm -rf /var/lib/apt/lists/*

# Create venv and install dependencies
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV="/opt/venv"

RUN /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install --no-cache-dir pytest click python-frontmatter

# Verify
RUN /opt/venv/bin/python -m pytest --version

RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

WORKDIR /source
COPY source_repo/ /source/
RUN npm install
RUN node bin/mdforge.js --version

# --- Zero-Test Environment ---
RUN rm -rf /source/tests/ /source/test/ /source/__tests__/ && \
    find /source -name "*.test.js" -delete && \
    find /source -name "*.spec.js" -delete && \
    find /source -name "test_*.js" -delete

# --- Anti-Cheating ---
RUN cd /source && \
    rm -rf .git && \
    git init && \
    git add -A && \
    git commit -m "source state - ready for translation" --quiet

RUN mkdir -p /target && \
    cd /target && \
    git init

RUN id user >/dev/null 2>&1 || useradd -m -u 1000 -s /bin/bash user
RUN chown -R user:user /source /target /opt/venv

USER user
WORKDIR /source