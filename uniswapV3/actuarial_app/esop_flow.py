import json
from datetime import datetime, timedelta
from pprint import pprint

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from actuarial_app.faker import fakeFintech
from actuarial_app.integration.yfi import Yfi
from actuarial_app.models.esop import BlackScholes as bs

pd.set_option("display.precision", 12)


# Code
# Steps to generate ESOP flow
# 1. Pull data related to a stock


def yahoo_pipline(ticker):
    yfi_client = Yfi(ticker=ticker)
    report_type = ["info", "balance_sheet", "income_stmt", "history"]
    return yfi_client.get_history(which=report_type[-1], period="max")


def esop_stock_hist(ticker):
    stock_hist = pd.DataFrame(yahoo_pipline(ticker=ticker))
    stock_hist["date"] = (
        pd.to_datetime(stock_hist["Date"], unit="ms", utc=True)
        .dt.strftime("%Y-%m-%d")
        .astype("datetime64[ns]")
    )

    stock_hist = stock_hist.assign(close_day_before=stock_hist.Close.shift(1))
    stock_hist["returns"] = (
        stock_hist.Close - stock_hist.close_day_before
    ) / stock_hist.close_day_before

    stock_hist["sigma"] = stock_hist["returns"].expanding(min_periods=1).std()
    stock_hist["sigma"] = stock_hist["sigma"].fillna(method="backfill")
    return stock_hist


# 2. Pull Users data related to ESOP scheme
def get_employee_data(company_srt_date=datetime.fromisoformat("2001-01-01")):
    ff = fakeFintech(
        datasize=100,
        company_found_date=company_srt_date,
        company="reliance.com",
        company_markercap=100000000,
        esop_scheme_prct=0.2,
    )
    return (
        ff.generate_esop_compensations()
        .sort_values(by="start_date")
        .reset_index(drop=True)
    )


# 3. Generate ESOP scheme option details
def get_esop_boosted_employee_info(employee_df: pd.DataFrame, stock_df: pd.DataFrame):
    """
    INPUT:
        df: Take the dataframe
    OUTPUT:
        new_df: Additional ESOP scheme info to add to the data
    """
    employee_df["start_date_epoch"] = (
        employee_df["start_date"] - datetime(1970, 1, 1)
    ).dt.total_seconds()

    stock_df["date_epoch"] = (
        stock_df["date"] - datetime(1970, 1, 1)
    ).dt.total_seconds()
    stock_df = stock_df.add_prefix("allocated_")
    boosted_df = pd.merge_asof(
        employee_df,
        stock_df,
        left_on="start_date_epoch",
        right_on="allocated_date_epoch",
    )

    # spot_price_by_join_date
    # strike_price: this is 20% discount on spot_price_by_join_date price
    # r -> The risk free rate: keeping at 4% but can be adjusted!
    boosted_df["strike_price"] = boosted_df["allocated_Close"] * 0.8
    boosted_df["allocated_option_value"] = boosted_df.apply(
        lambda x: bs(
            spot_price=x["allocated_Close"],
            strike_price=x["strike_price"],
            r=0.04,
            t=x["vesting_period"],
            sigma=x["allocated_sigma"],
        ).call,
        axis=1,
    )
    boosted_df["call_options_allocated"] = round(
        boosted_df["total_esop_offered"] / boosted_df["allocated_option_value"],
        0,
    )

    return boosted_df.sort_values(by="total_esop_offered", ascending=False)


def ts_esop_valuation(stock_df: pd.DataFrame, boosted_df: pd.DataFrame):
    """
    Calculate option value for each time between start date and today
    -
    left join stock market data on boosted employee data
    """

    df = stock_df.merge(boosted_df, how="cross")

    flag_employee_info = (~df["employee_id"].isna()) & (
        df["Date"] >= df["allocated_Date"]
    )
    emplyee_raw_esop = df[flag_employee_info].reset_index(drop=True)
    emplyee_raw_esop["vesting_period_delta"] = (
        -(emplyee_raw_esop["date"] - datetime.today()).dt.total_seconds() / 31556952
    ).astype(float)
    print(emplyee_raw_esop["vesting_period_delta"])
    emplyee_raw_esop["option_value"] = emplyee_raw_esop.apply(
        lambda x: bs(
            spot_price=x["Close"],
            strike_price=x["strike_price"],
            r=0.04,
            t=x["vesting_period_delta"],
            sigma=x["sigma"],
        ).call,
        axis=1,
    )

    return emplyee_raw_esop


def plot_esop_valuation(df):
    "Plot: BY date: esop valuation, total employees till that date,"
    agg = {"option_value": "sum", "Close": "min"}
    df_esop_plot = df.groupby(["date"]).agg(agg).reset_index()

    agg_e = {"employee_id": "nunique", "call_options_allocated": "min"}
    df_join_count = df.groupby(["start_date"]).agg(agg_e).reset_index()
    df_join_count["employee_count"] = df_join_count["employee_id"].cumsum()
    df_join_count["total_call_options_allocated"] = df_join_count[
        "call_options_allocated"
    ].cumsum()

    fig = go.Figure()
    fig = make_subplots(rows=3, cols=2)

    fig.add_trace(
        go.Scatter(
            x=df_esop_plot["date"],
            y=df_esop_plot["option_value"],
            mode="lines",
            name="ESOP option value",
            line_shape="spline",
            line_color="#ebb434",
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=df_esop_plot["date"],
            y=df_esop_plot["Close"],
            mode="lines",
            name="Reliance stock close",
            line_shape="spline",
            line_color="#ebb434",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df_join_count["start_date"],
            y=df_join_count["employee_count"],
            mode="lines",
            name="Reliance Employee count",
            line_shape="spline",
            line_color="#ebb434",
        ),
        row=3,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df_join_count["start_date"],
            y=df_join_count["total_call_options_allocated"],
            mode="lines",
            name="Total Call options_allocated",
            line_shape="spline",
            line_color="#ebb434",
        ),
        row=1,
        col=2,
    )

    # fig.add_trace(
    #     go.Scatter(
    #         x=df_join_count["maturity"],
    #         y=df_join_count["total_call_options_allocated"],
    #         mode="lines",
    #         name="Emplyee count",
    #         line_shape="spline",
    #     ),
    #     row=1,
    #     col=2,
    # )

    fig.update_layout(height=1200, width=1600, title_text="Side By Side Subplots")
    fig.show()


# 4. Calculate call price per user for all dates for all
# 5. Calculate ESOP valuation for each date


# Run
if __name__ == "__main__":
    TICKER = "RELIANCE.NS"
    # Steps to generate ESOP flow

    # [X] 1. Pull data related to a stock
    reliance_hist_stock = esop_stock_hist(ticker=TICKER)
    # pprint(reliance_hist_stock.head(10).to_dict(orient="records"))
    # pprint(reliance_hist_stock)

    # 2. Pull Users data related to ESOP scheme
    reliance_hist_users = get_employee_data()
    # pprint(reliance_hist_users.dtypes)
    # pprint(reliance_hist_users)

    reliance_hist_users_boosted = get_esop_boosted_employee_info(
        employee_df=reliance_hist_users, stock_df=reliance_hist_stock
    )

    ts_employee_esop = ts_esop_valuation(
        boosted_df=reliance_hist_users_boosted, stock_df=reliance_hist_stock
    )

    pprint(ts_employee_esop.shape)

    # 3. Generate ESOP scheme option details
    filter_user = ts_employee_esop.loc[0, "email"]
    print(filter_user)

    cond_user_filter = ts_employee_esop["email"] == filter_user

    plot_esop_valuation(df=ts_employee_esop)

    # 4. Calculate call price per user for all dates for all
    # 5. Calculate ESOP valuation for each date
