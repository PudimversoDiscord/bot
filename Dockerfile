FROM python:3.12-slim

WORKDIR /app

RUN python -m pip install --no-cache-dir -U pip setuptools wheel
RUN python -m pip install --no-cache-dir pdm

COPY pyproject.toml pdm.lock ./
RUN pdm export --prod -o requirements.txt && python -m pip install --no-cache-dir -r requirements.txt

COPY pdx/ pdx/
RUN python -m pip install --no-cache-dir .

CMD [ "python", "-m", "pdx" ]