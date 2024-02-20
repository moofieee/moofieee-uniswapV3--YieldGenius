# Imlpement black sholes model
import datetime
from pprint import pprint

import numpy as np
import pandas as pd
from ydata_profiling import ProfileReport

from actuarial_app.faker import fakeFintech

ff = fakeFintech(
    datasize=100,
    company_found_date=datetime.datetime.fromisoformat("2022-01-01"),
    company="reliance.com",
    company_markercap=100000000,
    esop_scheme_prct=0.2,
)


# reliance = ff.generate_esop_compensations()
# profile = ProfileReport(reliance, title="reliance employee Profiling Report")
# profile.to_file("db/reports/reliance_report.html")
