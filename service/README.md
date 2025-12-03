# Nutrition Digital Twin API

Minimal FastAPI service exposing recommend/feedback endpoints.

## Install (Windows PowerShell)

```powershell
cd "D:\Documents\Diet plan"
.\.venv\Scripts\Activate.ps1
pip install fastapi uvicorn pydantic
```

## Run

```powershell
uvicorn service.api:app --host 0.0.0.0 --port 8000 --reload
```

## Example cURL

```powershell
$body = @{
  age=28; sex="male"; bmi=24.5; region="north_indian"; diet_type="veg"; activity="moderate"; weight_class="normal"; conditions=@("pcos")
} | ConvertTo-Json

curl -X POST "http://localhost:8000/recommend" -H "Content-Type: application/json" -d $body
```
