# ModelDeployment_FastAPI

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
def ping():
    return 'pong'
```