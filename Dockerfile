# Stage 1: Build the frontend
FROM node:20-slim AS build-stage
WORKDIR /ui-build
COPY university-advisor-ui/package*.json ./
RUN npm install
COPY university-advisor-ui/ ./
RUN npm run build

# Stage 2: Python environment
FROM python:3.11-slim

# Install system dependencies for sentence-transformers/chromadb if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"
WORKDIR /app

# Install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy backend code and data
COPY --chown=user . .

# Copy built frontend from build-stage to 'static' folder
COPY --chown=user --from=build-stage /ui-build/dist /app/static

# Ensure data directories exist and have correct permissions
# (COPY --chown handles this mostly, but good to be explicit if they are created at runtime)
# RUN mkdir -p chroma_db data

# Expose port 7860
EXPOSE 7860

# Run the app
CMD ["python", "self_rag_agent.py"]
