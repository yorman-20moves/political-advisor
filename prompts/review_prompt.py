# File: review_prompt.py
# Directory: my_app/prompts/

# Overall Role and Purpose:
# - Defines the `REVIEW_PROMPT` template.
# - Guides the LLM to review the extracted data for accuracy and completeness.

# Expected Inputs:
# - Extracted data to be reviewed.

# Expected Outputs:
# - A formatted prompt string ready for use with the LLM.


REVIEW_PROMPT = """
You are a data reviewer. Review the following extracted data for quality and correctness.

Extracted Data:
{extracted_data}

Instructions:
- Check for completeness and accuracy.
- Ensure all required fields are present and correctly formatted.
- If the data is valid, respond with "Valid".
- If there are issues, list the problems found.

Output:
"""
