### Clone the repository
```
   git clone https://github.com/abhinav-vasudevan/Digital-Twin/
   git checkout feature/three-recommendation-systems/
```


### Create a python venv and activate it
```python -m venv .venv```

##### if on windows:
```.venv\Scripts\Activate.ps1```

##### if on nix-based:
```source .venv/bin/activate```

### Install python3 dependencies
```pip install -r requirements.txt```

### Run the server
```python -m uvicorn service.api:app --reload --port 8000```


### ML model
It is better to have the server running on colab from my end as I have access to
hidden repositories from hugging face and all the authentication tokens for ngrok and hugging face are
already properly setup from my side
