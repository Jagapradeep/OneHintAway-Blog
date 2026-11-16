# Builds the site the same way on every machine: Node 22 (as in .node-version and the
# Cloudflare build), a clean `npm ci`, then `npm run build` (post check, visualizer check,
# Next.js static export). Production is still served by Cloudflare; this image is for CI.
#
#   docker build -t onehintaway-site:local .                 (run from site/)
#   docker build --output type=local,dest=out-docker .       copy the built files out instead

# ---- 1. deps: node_modules, rebuilt only when the lock file changes ---------------------
FROM node:22-bookworm-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# ---- 2. build: checks + static export into /app/out -------------------------------------
FROM deps AS build
ENV NEXT_TELEMETRY_DISABLED=1
# The API address is baked into the pages at build time. It is public, not a secret.
# Empty (the default) = every API extra is off, exactly like production today.
ARG NEXT_PUBLIC_API_URL=""
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
COPY . .
RUN npm run build

# ---- 3. export: only the finished files, no Node, no node_modules -----------------------
FROM scratch AS export
COPY --from=build /app/out/ /
