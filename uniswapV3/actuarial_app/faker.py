import datetime
import random
from dataclasses import dataclass
from pprint import pprint

import numpy as np
import pandas as pd
from faker import Faker

# [ ] Given a size of data and types of columns, we generate the dataset on the fly
org_chart = {
    "departments": [
        "Devops",
        "Sales",
        "Platform",
        "Product",
        "HR",
        "operations",
        "marketing",
    ],
    "titles": {
        "Devops": ["staff Engineer", "Engineer", "Senior Engineer", "Manager"],
        "Sales": [
            "Associate",
            "Engineer",
            "Senior Engineer",
            "Manager",
            "Director",
        ],
        "Platform": ["Associate", "Engineer", "Senior Engineer", "Manager"],
        "operations": [
            "Analyst",
            "Senior Analyst",
            "Manager",
            "VP",
            "Director",
        ],
        "Product": ["Analyst", "Senior Analyst", "Manager", "VP", "Director"],
        "HR": [
            "staff Engineer",
            "Engineer",
            "Senior Engineer",
            "VP",
            "Manager",
            "Director",
        ],
        "marketing": ["Manager", "VP", "Engineer"],
        "management": ["CEO", "CTO"],
    },
    "levels": [1, 2, 3, 4, 5],
    "salary_range": {
        "staff Engineer": [120, 180],
        "Engineer": [90, 120],
        "Senior Engineer": [110, 140],
        "Manager": [130, 150],
        "Associate": [60, 80],
        "Analyst": [60, 80],
        "Senior Analyst": [80, 120],
        "VP": [150, 250],
        "Director": [250, 350],
        "management": [300, 500],
    },
    "levels_factor": [0.5, 0.6, 0.7, 0.8, 1],
}


@dataclass
class fakeFintech:
    """
    What is the bound of this class
    - generate dataset based on the parameters provided
    - Input size: 1- 100000
    - type of data needed(json,df etc)

    INPUTS:
    - datasize: Data size between: [1- 10000 ]
    - columns: type of data columns needed
        - standard profile
        - jobs as per
    OUTPUT:
    """

    fake = Faker()
    datasize: int
    company_found_date: datetime.datetime
    company: str
    company_markercap: int
    esop_scheme_prct: float

    def org_hierarchy(self):
        """
        # Logic:
        - based on size:
        - 1 CEO, 1 CTO, everything else can be random
        """
        return {"CEO": 1, "CTO": 1, "Other": self.datasize - 1}

    def basic_info(self):
        g = "M" if random.randint(0, 1) == 0 else "F"
        n = self.fake.first_name_male() if g == "M" else self.fake.first_name_female()
        ln = self.fake.last_name()
        return {
            "employee_id": self.fake.uuid4(),
            "gender": g,
            "first_name": n,
            "last_name": ln,
            "email": f"{n.lower()}.{ln.lower()}@{self.company}",
        }

    def birth_and_start_date(self):
        sd = self.fake.date_between(start_date=self.company_found_date, end_date="now")
        delta = datetime.timedelta(days=365 * random.randint(18, 40))
        bd = sd - delta
        vesting_period = random.randint(3, 4)
        cliff = random.randint(1, 2)
        maturity = sd + datetime.timedelta(days=365 * vesting_period)

        return {
            "birth_date": bd,
            "start_date": sd,
            "vesting_period": vesting_period,
            "cliff": cliff,
            "maturity": maturity,
        }

    def org_title_office_lvl(self):
        dept = random.choice(org_chart["departments"])
        title = random.choice(org_chart["titles"][dept])
        level = random.choice(org_chart["levels"])
        salary = (
            1000
            * random.choice(org_chart["salary_range"][title])
            * org_chart["levels_factor"][level - 1]
        )

        return {"dept": dept, "title": title, "level": level, "salary": salary}

    def generate_employee_info(self):
        """
        OUTPUT:
        the final output should have following columns
        [
            "id",
            "first_name",
            "last_name",
            "gender",
            "email",
            "dob",
            "company_start_date", #- CEO,CTO started early
            "start_date",
            "title",
            "department",
            "join_date",
            "strike_price", #- early joined gets better price
            "cliff_period",
            "exercise_period",
            "vesting_schedule"
            "fmv_discount_prct" # - % discount to fair price/stock price on that date
            ""
        ]
        """
        info = []
        d = dict()
        d["basic_info"] = self.basic_info
        d["birth_and_start_date"] = self.birth_and_start_date
        d["title_office_org_salary_bonus"] = self.org_title_office_lvl

        for i in range(self.datasize):
            deep_list = [d[k]() for k in d.keys()]
            data = {k: v for e in deep_list for (k, v) in e.items()}

            info.append(data)
        return pd.DataFrame(info)

    def generate_esop_compensations(self):
        """
        - Adding salary based on level and title
        - Adding stock options based on

        """
        df_info = self.generate_employee_info()
        salary_total = df_info["salary"].sum()

        df_info["total_esop_offered"] = round(
            (df_info["salary"] / salary_total)
            * self.company_markercap
            * self.esop_scheme_prct,
            -2,
        )
        df_info["esop_offered_year"] = (
            df_info["total_esop_offered"] / df_info["vesting_period"]
        )
        type_schema = {
            "gender": "category",
            "birth_date": "datetime64[s]",
            "start_date": "datetime64[s]",
            "maturity": "datetime64[s]",
            "vesting_period": int,
            "cliff": int,
            "total_esop_offered": int,
            "dept": "category",
            "level": "category",
        }

        return df_info.astype(type_schema)
