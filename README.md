# 1 ModelDeployment_FastAPI

Download starter.ipynb notebook
```
wget https://raw.githubusercontent.com/alexeygrigorev/workshops/main/mlzoomcamp-fastapi-uv/starter.ipynb -O workshop-uv-fastapi.ipynb
```


Install the libraries

```
pip install jupyter scikit-learn pandas numpy

```

Execute Jupyter notebook

```
jupyter notebook

```

we build the model then convert jupyternotebook to script

```
jupyter nbconvert --to=script workshop-uv-fastapi.ipynb 
```

now we split the script into train.py and predict.py
and we install

```
pip install fastapi uvicorn

```

we will create a simple web application ping.py 
```
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="ping")

@app.get("/ping")
def ping():
    return "PONG"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9696)

```

to get response 

```
curl localhost:9696/ping

```


customer= {
    'gender': 'male',
  'seniorcitizen': 0,
  'partner': 'no',
  'dependents': 'yes',
  'phoneservice': 'no',
  'multiplelines': 'no_phone_service',
  'internetservice': 'dsl',
  'onlinesecurity': 'no',
  'onlinebackup': 'yes',
  'deviceprotection': 'no',
  'techsupport': 'no',
  'streamingtv': 'no',
  'streamingmovies': 'no',
  'contract': 'month-to-month',
  'paperlessbilling': 'yes',
  'paymentmethod': 'electronic_check',
  'tenure': 6,
  'monthlycharges': 29.85,
  'totalcharges': 129.85
}

To see the changes in the app: In terminal
```
uvicorn predict:app --host 0.0.0.0 --port 9696 --reload

```

to check churn in termina

```
curl -X 'POST' \
  'http://localhost:9696/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "gender": "male",
  "seniorcitizen": 0,
  "partner": "no",
  "dependents": "yes",
  "phoneservice": "no",
  "multiplelines": "no_phone_service",
  "internetservice": "dsl",
  "onlinesecurity": "no",
  "onlinebackup": "yes",
  "deviceprotection": "no",
  "techsupport": "no",
  "streamingtv": "no",
  "streamingmovies": "no",
  "contract": "month-to-month",
  "paperlessbilling": "yes",
  "paymentmethod": "electronic_check",
  "tenure": 6,
  "monthlycharges": 29.85,
  "totalcharges": 129.85
}'
```


for marketing.py we install the library
```
pip install requests

```
# 2 Virtual enviroment
for virtual enviroment we will use uv which is faster than venv

```
pip install uv
```

then we activate with

```
uv init

```

we see two new files .python-version and pyproject.toml

we can add for now only the libraries needed for predicting

```
uv add scikit-learn fastapi uvicorn

```

now we have in .toml the new dependencies and uv.lock is added 

```
uv add --dev requests
```

to run the web service:

```
 uv run uvicorn predict:app --host 0.0.0.0 --port 9696 --reload
 
 ```

 in the other terminal we run the marketing response:

 ```
uv run python marketing.py

 ```

 # 3 Contenarization:

 To check if we have docker : 

 ```
docker run hello world

 ```

 we create a Dockerfile
 ```
FROM python:3.12.1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked

COPY predict.py model.bin ./

EXPOSE 9696

ENTRYPOINT ["uvicorn", "predict:app", "--host", "0.0.0.0", "--port", "9696"]
 ```

 To run the script from docker locally

 ```
docker build -t churn-prediction .

 ```

To run locally using docker
```
 docker run -t --rm -p 9696:9696 churn-prediction

 ```