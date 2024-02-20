# Along with vanila implentation
import datetime
from dataclasses import dataclass
from datetime import datetime as dt
from math import exp, log, pi, sqrt
from pprint import pprint

import numpy as np
import pandas as pd
from scipy.stats import norm

# not using currently: import pyfeng as pf


@dataclass
class BlackScholes:
    """
    ESOP offered at sd discount:
    definitions: https://cleartax.in/s/taxation-on-esop-rsu-stock-options
    Time between vesting and exercise is 1 month
    INPUTS:
    """

    spot_price: float
    strike_price: float
    r: float
    sigma: float
    t: float

    # S= spot price of an asset
    # K = strike price
    # r = risk-free interest rate
    # t = time to maturity
    # σ = volatility of the asset

    risk_free_ir: float = 4.5

    def d1(self):
        return (
            log(self.spot_price / self.strike_price)
            + (self.r + self.sigma**2 / 2.0) * self.t
        ) / (self.sigma * sqrt(self.t))

    def d2(self):
        return self.d1() - self.sigma * sqrt(self.t)

    @property
    def call(self):
        return self.spot_price * norm.cdf(self.d1()) - self.strike_price * exp(
            -self.r * self.t
        ) * norm.cdf(self.d2())

    @property
    def put(self):
        return self.strike_price * exp(-self.r * self.t) - self.spot_price + self.call


# EG
# bs = BlackScholes(
#     strike_price=300,
#     spot_price=427.53,
#     r=0.025,
#     t=4 / 365,
#     sigma=0.6,
# )

# option_value = bs.call
# esop_option_valuation = 757 * option_value
# pprint(f"option value: {option_value}")
# pprint(f"Total ESOP value: {esop_option_valuation}")
