import dlt
<<<<<<< HEAD
from dlt.sources.helpers import requests
import pandas as pd
from dlt.common.libs.pydantic import pydantic_to_table_schema_columns
from actuarial_app import models



@dlt.resource(
    table_name="history",
    write_disposition="replace",
    columns=pydantic_to_table_schema_columns(models.MakerburnHistory),
    )
def makerburn_history(URL_history: str = dlt.config.value):
    response = requests.get(URL_history)
=======
import pandas as pd
from dlt.common.libs.pydantic import pydantic_to_table_schema_columns
from dlt.sources.helpers import requests

from actuarial_app.helper import models
from actuarial_app.integration.urls import makerburn as url


@dlt.resource(
    table_name="makerburn_history",
    write_disposition="replace",
    columns=pydantic_to_table_schema_columns(models.MakerburnHistory),
)
def makerburn_history():
    response = requests.get(url["MAKERBURN_URL_HIST"])
>>>>>>> 25bbaf56a11039b0726734fbb292f0c084475264
    response.raise_for_status()
    yield response.json()


<<<<<<< HEAD

=======
>>>>>>> 25bbaf56a11039b0726734fbb292f0c084475264
@dlt.resource(
    table_name="makerburn_collateral_list",
    write_disposition="replace",
    columns=pydantic_to_table_schema_columns(models.MakerburnCollateralList),
<<<<<<< HEAD
    )
def collateral_list(URL_status: str = dlt.config.value):
    
    response = requests.get(URL_status)
    response.raise_for_status()
    data = response.json()
    yield data['collateral_list']


# after getting this just pull the id's and loop it to the history 
@dlt.transformer(
    data_from=collateral_list,
    table_name="collateral_history",
    write_disposition="replace",
    columns=pydantic_to_table_schema_columns(models.CollateralHistory))
def collateral_history(collaterallist, URL_history: str = dlt.config.value):
    collateral_hist = []
    df = pd.DataFrame(collaterallist)
    for ilk, name in zip(list(df['type']), list(df['name'])):
        hist_url = f"{URL_history}/{ilk}"
        response = requests.get(hist_url)
        response.raise_for_status()
        data = response.json()
        history = data['history']
        
        for day in history:
            day['name'] = name
        collateral_hist.extend(history)
    
    yield collateral_hist
        

=======
)
def collateral_list(makerburn_url_status=dlt.config.value):
    response = requests.get(url["MAKERBURN_URL_STATUS"])
    response.raise_for_status()
    data = response.json()
    yield data["collateral_list"]


# after getting this just pull the id's and loop it to the history
@dlt.transformer(
    data_from=collateral_list,
    table_name="makerburn_collateral_history",
    write_disposition="replace",
    columns=pydantic_to_table_schema_columns(models.CollateralHistory),
)
def collateral_history(
    collaterallist,
):
    for collatoral in collaterallist:
        print(f"Pulling data for {collatoral['type']}")
        makerburn_url_history = url["MAKERBURN_URL_HIST"]
        hist_url = f"{makerburn_url_history}/{collatoral['type']}"
        response = requests.get(hist_url)
        response.raise_for_status()
        data = response.json()
        history = data["history"]
        for day in history:
            day["name"] = collatoral["type"]

            for key in day:
                day[key] = str(day[key])

            print(f"for {collatoral['type']}: {day}")
        yield history
>>>>>>> 25bbaf56a11039b0726734fbb292f0c084475264


@dlt.source(max_table_nesting=0)
def makerburn_raw():
<<<<<<< HEAD
    return [
        makerburn_history,
        collateral_list,
        collateral_history
        ]
=======
    return [makerburn_history, collateral_list, collateral_history]
>>>>>>> 25bbaf56a11039b0726734fbb292f0c084475264


def makerburn_pipeline() -> None:
    p = dlt.pipeline(
<<<<<<< HEAD
        pipeline_name="makerburn",
        destination="duckdb",
        dataset_name="makerburn_raw",
        # credentials=dlt.secrets.value,
=======
        pipeline_name="makeburn",
        destination="bigquery",
        dataset_name="raw",
        credentials=dlt.secrets.value,
>>>>>>> 25bbaf56a11039b0726734fbb292f0c084475264
    )
    print("pipeline running")
    p.run(makerburn_raw())


<<<<<<< HEAD

if __name__ == "__main__":

    
    makerburn_pipeline()
    
=======
if __name__ == "__main__":
    print(makerburn_pipeline())
>>>>>>> 25bbaf56a11039b0726734fbb292f0c084475264
