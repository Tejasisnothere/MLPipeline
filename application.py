from fastapi import FastAPI, Request
import os
from dotenv import load_dotenv
import sys
import pandas as pd
import numpy as np
from pydantic import BaseModel
from src.exception import CustomException
from src.logger import logging
from src.components.dataIngestion import DataIngestionPipeline
from fastapi.templating import Jinja2Templates
import uvicorn
from src.components.graphPipeline import GraphPipeline
from datetime import datetime, timedelta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

application = FastAPI()

app = application


from pydantic import BaseModel

class GraphRequest(BaseModel):
    category: str       # The category selected by the user
    graph_type: str    

def dataframe_to_graph(df):
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date', ignore_index=True)
        return {
            "x": df['date'].dt.strftime("%Y-%m-%d").tolist(),
            "y": df['profit'].tolist()
        }




@app.get('/predict/{inv_id}')
def predict(inv_id):
    dip = DataIngestionPipeline()
    output = dip.get_data(inv_id=inv_id)

    return {"success":"True", "data":output}



@app.get('/graph/{inv_id}/{category}')
async def graph(inv_id, request: Request):
    dip = DataIngestionPipeline()
    output = dip.get_data(inv_id=inv_id)
    gp = GraphPipeline()
    graph_data = gp.direct_dataframe_to_graph()
    
    return templates.TemplateResponse("graph.html", {"request": request, "data": graph_data})
    
@app.post("/graph-data/{inv_id}")
async def get_graph_data(inv_id, req: GraphRequest):
    dates = [datetime.now() - timedelta(days=i) for i in range(30)][::-1]

    if req.category == "category1":
        values = np.random.randint(50, 100, size=30)
    elif req.category == "category2":
        values = np.random.randint(100, 200,  size=30)
    else:
        values = np.random.randint(10, 50, size=30)

    df = pd.DataFrame({"ds": dates, "y": values})
    return {
        "data": dataframe_to_graph(df),
        "graph_type": req.graph_type
    }



@app.get('/displayGraph')
async def home(request: Request):
    pass


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  
    uvicorn.run("application:app", host="0.0.0.0", port=port, reload=True)