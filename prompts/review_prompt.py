# File: review_prompt.py
# Directory: my_app/prompts/

# Overall Role and Purpose:
# - Defines the `REVIEW_PROMPT` template.
# - Guides the LLM to review the extracted data for accuracy and completeness.

# Expected Inputs:
# - Extracted data to be reviewed.

# Expected Outputs:
# - A formatted prompt string ready for use with the LLM.

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

REVIEW_SYSTEM_PROMPT = """
You are tasked with reviewing the following JSON data. Analyze it based on the following criteria:

**1. Syntax**:
- Verify that the JSON structure is valid and free from syntax errors.
- If invalid, specify the incorrect syntax and provide the corrected version.

**2. Entity Classification**:
- Check if the data is correctly categorized into entities such as Person, Event, Institution, etc.
- If any entity is incorrectly classified, explain the error and suggest the correct classification.

**3. Relationship Accuracy**:
- Ensure the relationships between entities (e.g., is_author, is_employed_by, participated_in) are logically accurate based on the context.
- If relationships are incorrect, describe the issue and suggest the correct relationship.

**4. Consistency**:
- Ensure fields such as dates, participants, and quotes follow consistent formats and are appropriately filled.
- If inconsistencies are found, describe them and suggest corrections.

**For each identified issue, include**:
- The specific problem (syntax, classification, relationship, or consistency).
- A brief description of the issue.
- The proposed correction or reclassification.

**If everything is valid**, confirm that no issues were found.

Your output should follow this structure:

```json
{
    "Review": {
        "Syntax": {
            "Status": "Valid" or "Invalid",
            "Errors": [
                {"Problem": "Describe syntax issue", "Correction": "Provide corrected syntax"}
            ]
        },
        "Entity Classification": {
            "Status": "Valid" or "Invalid",
            "Errors": [
                {"Problem": "Describe classification issue", "Correction": "Provide corrected classification"}
            ]
        },
        "Relationship Accuracy": {
            "Status": "Valid" or "Invalid",
            "Errors": [
                {"Problem": "Describe relationship issue", "Correction": "Provide corrected relationship"}
            ]
        },
        "Consistency": {
            "Status": "Valid" or "Invalid",
            "Errors": [
                {"Problem": "Describe consistency issue", "Correction": "Provide corrected consistency"}
            ]
        }
    }
}

"""

REVIEW_HUMAN_PROMPT = """
{extracted_data}
"""

REVIEW_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", REVIEW_SYSTEM_PROMPT),
        ("human", REVIEW_HUMAN_PROMPT),
    ]
)

ReviewPrompt = ChatPromptTemplate.from_messages(
    [
        ("system", REVIEW_SYSTEM_PROMPT),
        ("human", REVIEW_HUMAN_PROMPT),
    ]
)
