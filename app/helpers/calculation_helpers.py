from num2words import num2words
from typing import Dict
from datetime import datetime, timedelta


def calculate_derived_fields(record: Dict[str, str]) -> Dict[str, str]:
    def to_float(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    try:
        earnings_keys = ["Basic", "Allowances", "Bonus"]
        deductions_keys = ["PF", "PT", "TDS", "Arrears"]

        total_earnings = sum(to_float(record.get(k, 0)) for k in earnings_keys)
        total_deductions = sum(to_float(record.get(k, 0)) for k in deductions_keys)
        basic = to_float(record.get('Basic'))
        net_salary = basic - total_deductions

        try:
            net_salary_words = num2words(net_salary, to='currency', lang='en_IN').replace('euro', 'rupees').title() + " Only"
        except Exception:
            net_salary_words = "Conversion error"

        previous_month = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%B %Y')

        record["Total_Earnings"] = f"{total_earnings:.2f}"
        record["Total_Deductions"] = f"{total_deductions:.2f}"
        record["Net_Salary"] = f"{net_salary:.2f}"
        record["Net_Salary_In_Words"] = net_salary_words
        record["Month"] = previous_month

    except Exception as e:
        record["Error"] = f"Error calculating derived fields: {str(e)}"

    return record
