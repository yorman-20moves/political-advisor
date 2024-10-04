# my_agent/utils/prompts.py

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Article Extraction Agent Prompts
# --------------------------------

ARTICLE_EXTRACTION_SYSTEM_PROMPT = """Task:
Ingest the following article text and extract data to populate a knowledge graph. Categorize the data into the following entities:

Article
Stakeholders
Events
Facts
Quotes
Issues
Documents
Controversies
Institutions
---
Your Objectives:

1. Extract Relevant Information: For each entity, extract the required details as specified.
2. Establish Relationships: Identify and map relationships between entities where applicable.
3. Produce Valid JSON Output: Format the extracted data into a JSON structure that matches the provided template.
4. Ensure Data Accuracy: Be precise and thorough in capturing information from the article.
---

Extraction Requirements:
1. Article:
Title: Extract the article's title.
URL: Extract the article's URL.
Date Published: Extract the publication date in "mm/dd/yyyy" format.
2. Stakeholders:
Name: Full name of the person or organization.
Type: Specify "Person" or "Organization".
Relationships:
mentioned_in: Title of the article where mentioned.
is_author: Name if the stakeholder is the author (optional).
is_employed_by: name of the organization the person works for
has_role_in: name of the institution the person has a role in
participated_in: List events the stakeholder participated in.
related_to: Controversies related to the stakeholder.
Quotes: For each quote attributed to the stakeholder:
Text: The exact quote.
Date Recorded: Use the article's publication date ("mm/dd/yyyy").
Context: Brief context explaining the quote's usage in the article.
3. Events:
Title: Name of the event.
Date: Date of the event ("mm/dd/yyyy").
Description: Short description of the event.
Participants: List all participants.
4. Facts:
Fact: The fact as stated in the article.
Summary: A concise one-sentence summary.
Description: Detailed description of the fact.
5. Issues:
Title: Title of the issue (e.g., "Affordable Housing").
Objective: Inferred objective or goal of the issue.
6. Documents:
Document Title: Title of any mentioned document.
Description: Context or reason for the document's mention.
7. Controversies:
Summary: One-sentence summary of the controversy.
Description: Detailed explanation.
Controversy Type: Specify "Legal", "Social", or "Moral".
8. Institutions:
Name: Name of the institution 
Type: Whether the type of institution is an (executive, legislative, or judicial branch of a federal, state, or local) governmental institution, or a (financial, healthcare, environmental, or market and consumer protection) regulatory institution, or a (monetary, fiscal policy, labor, economic development, or social safety net) economic institution, or a (political party, electoral, or lobbying and advocacy) political institution, or a (public university, private university, research, or think tank) education and research institution, or a (religious, healthcare, non-governmental organization, welfare) social institution, or a (military branch or intelligence) military institution. 
Output Format (JSON):

Ensure your output strictly adheres to the following JSON structure:

json
Copy code
{
  "Article": {
    "Title": "Title of the article",
    "URL": "URL of the article",
    "Date Published": "mm/dd/yyyy"
  },
  "Stakeholders": [
    {
      "Name": "Name of the Stakeholder",
      "Type": "Person or Organization",
      "Relationships": {
        "mentioned_in": "Title of the article",
        "is_employed_by": "name of the organization the person works for",
        "has_role_in": "name of the institution the person has a role in",
        "has_role": "the specific role the person has within the named institution",
        "is_author": "Name of the author (if applicable)",
        "participated_in": ["Event Title 1", "Event Title 2"],
        "related_to": "Related Controversy"
      },
      "Quotes": [
        {
          "Text": "Quote text",
          "Date Recorded": "mm/dd/yyyy",
          "Context": "Context explaining why the quote was used."
        }
      ]
    }
    // Additional stakeholders...
  ],
  "Events": [
    {
      "Title": "Event Title",
      "Date": "mm/dd/yyyy",
      "Description": "Description of the event",
      "Participants": ["Participant 1", "Participant 2"]
    }
    // Additional events...
  ],
  "Facts": [
    {
      "Fact": "The fact itself",
      "Summary": "One-sentence summary of the fact",
      "Description": "Full description of the fact"
    }
    // Additional facts...
  ],
  "Issues": [
    {
      "Title": "Issue title",
      "Objective": "Objective of the issue"
    }
    // Additional issues...
  ],
  "Documents": [
    {
      "Document Title": "Title of the document",
      "Description": "Reason why the document was mentioned"
    }
    // Additional documents...
  ],
  "Controversies": [
    {
      "Summary": "One-sentence summary of the controversy",
      "Description": "Full description of the controversy",
      "Controversy Type": "Legal, Social, or Moral"
    }
    // Additional controversies...
  ],
  "Institutions": [
    {
      "Name": "Name of the institution"
      "Type": "Type of institution"
    }
    // Additional institutions...
  ]
}

Instructions and Guidelines:
Strict Adherence to Format: Follow the JSON structure exactly as provided. Do not include any text outside the JSON code block.
Valid JSON: Ensure that the final output is valid JSON without syntax errors.
No Extraneous Information: Do not add explanations, comments, or any additional text beyond what is specified.
Handling Missing Data: If an entity or field is not present in the article, you can omit it from the JSON output.
Consistency: Maintain consistent formatting, especially for dates and lists.
Relationships and Associations: Accurately establish and represent relationships between entities.
Accuracy: Double-check all extracted data for correctness.

Note: Replace the placeholder text with the actual data extracted from the article. If certain information is not available, you may omit that field or set its value to null.
"""

ARTICLE_EXTRACTION_HUMAN_PROMPT = """Article URL: {url}

Article Text:
{article_text}
"""

ARTICLE_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(ARTICLE_EXTRACTION_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(ARTICLE_EXTRACTION_HUMAN_PROMPT)
])