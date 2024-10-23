FROM python:3.12-slim
COPY requirements.txt app/requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ,"--reload"]
