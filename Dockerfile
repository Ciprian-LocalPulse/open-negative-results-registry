# Dark Data Medicine — CLI toolkit container
#
# Packages the project's validation, analysis, export, and indexing
# scripts into a single, dependency-free-to-run image, so curators
# and contributors can use the tooling without a local Python setup.
#
# Build locally:
#   docker build -t darkdata-medicine .
#
# Run (validate the dataset shipped in the image):
#   docker run --rm darkdata-medicine validate data/
#
# Run against your own data, mounted from the host:
#   docker run --rm -v "$PWD/data:/app/data" darkdata-medicine validate data/
#   docker run --rm -v "$PWD/data:/app/data" darkdata-medicine analyze --top 20
#   docker run --rm -v "$PWD:/app/out" darkdata-medicine export --output /app/out/DarkData.xlsx

FROM python:3.12-slim AS base

LABEL org.opencontainers.image.title="Dark Data Medicine CLI" \
      org.opencontainers.image.description="Validation, analysis, export, and search-index tooling for the Dark Data Medicine open negative-results registry." \
      org.opencontainers.image.source="https://github.com/Ciprian-LocalPulse/open-negative-results-registry" \
      org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install only what the scripts need (see requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the toolkit and the dataset it ships with by default
COPY scripts/ ./scripts/
COPY data/ ./data/
COPY site/ ./site/

# Non-root user for safer default execution
RUN useradd --create-home --uid 1000 curator
USER curator

# Single entrypoint script dispatches to the right tool
COPY --chown=curator:curator docker-entrypoint.sh /app/docker-entrypoint.sh
USER root
RUN chmod +x /app/docker-entrypoint.sh
USER curator

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["--help"]
