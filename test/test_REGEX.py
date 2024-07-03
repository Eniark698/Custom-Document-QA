# Expected JSON format result
import json
import re

# Simple regex-based extraction (for demonstration purposes, replace with proper parsing if needed)
reporting_period_match = re.search(r"з «(\d{2})» (\w+) (\d{4}) року по «(\d{2})» (\w+) (\d{4}) року", text)
final_sum_match = re.search(r"складає (\d+ грн\. \d+ коп\.)", text)

reporting_period = None
final_sum = None

if reporting_period_match:
   reporting_period = f"{reporting_period_match.group(1)}.{reporting_period_match.group(2)}.{reporting_period_match.group(3)} - {reporting_period_match.group(4)}.{reporting_period_match.group(5)}.{reporting_period_match.group(6)}"
if final_sum_match:
   final_sum = final_sum_match.group(1)

# Create JSON object
result = {
   "reportingPeriod": reporting_period,
   "finalSum": final_sum
}

# Print the JSON result
print(json.dumps(result, ensure_ascii=False, indent=4))