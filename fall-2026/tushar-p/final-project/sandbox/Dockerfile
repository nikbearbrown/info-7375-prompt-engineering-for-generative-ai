# Sandbox image for task runs. Build: docker build -t apg-sandbox:dev sandbox/
FROM python:3.12-slim

# pytest pinned so check results do not change when a new release ships.
RUN pip install --no-cache-dir pytest==9.2.0

# Non-root user with uid 1000 (matches runAsUser: 1000 in the pod spec).
# /workspace is where the task repo is copied in; the user must own it.
RUN useradd --uid 1000 --create-home apg \
    && mkdir /workspace \
    && chown 1000:1000 /workspace

# Do not write __pycache__ files into the workspace.
ENV PYTHONDONTWRITEBYTECODE=1

USER 1000
WORKDIR /workspace

# Keep the container alive; the harness runs commands in it with kubectl exec.
CMD ["sleep", "infinity"]
