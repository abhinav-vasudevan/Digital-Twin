### Clone the repository
git clone https://github.com/abhinav-vasudevan/Digital-Twin/

### Create a python venv and activate it
python -m venv .venv

##### if on windows:
.venv\Scripts\Activate.ps1

##### if on nix-based:
source .venv/scripts/activate

### Install python3 dependencies
pip install -r requirements.txt

### Run the server
python -m uvicorn service.api:app --reload --port 8000


### Running the ML model
The ML model runs on google colab and uses ngrok to expose the API endpoints of the LLM using FastAPI.
For this upload the python notebook from notebooks/Colab_Llama_FoodModel.ipynb to google colab and run it
with your preferred GPU.
