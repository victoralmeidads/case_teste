from fastapi import FastAPI, HTTPException

from src.analytics.analysis import generate_insights
from src.business.metrics import calculate_indicators
from src.ingestion.simulated_api import SimulatedEandPApiSource
from src.transformation.quality import normalize_and_validate


app = FastAPI(
    title="IPNOD | Dados Operacionais E&P",
    description="API demonstrativa para integracao de indicadores de producao.",
    version="1.0.0",
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "ipnod-ep-analytics"}


@app.get("/production")
def production():
    try:
        source = SimulatedEandPApiSource()
        quality = normalize_and_validate(source.load())
        return calculate_indicators(quality.data).to_dict(orient="records")
    except (ValueError, KeyError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/insights")
def insights():
    source = SimulatedEandPApiSource()
    quality = normalize_and_validate(source.load())
    frame = calculate_indicators(quality.data)
    return {"insights": generate_insights(frame), "source": source.name}