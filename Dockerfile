FROM python:3.12-slim
WORKDIR /app

RUN pip install --no-cache-dir --root-user-action ignore poetry
COPY . .

RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi


EXPOSE 8080
CMD ["poetry", "run", "python", "mintwit/app.py"]
