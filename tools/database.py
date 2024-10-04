# File: database.py
# Directory: my_app/tools/

# Overall Role and Purpose:
# - Contains the `KnowledgeGraphUploader` class.
# - Handles the connection and transactions with the Neo4j database.
# - Executes Cypher queries to merge nodes and relationships.
# - Logs details of each upload.

# Expected Inputs:
# - Structured data to upload.
# - Database connection details from the configuration.

# Expected Outputs:
# - Inserts data into the knowledge graph.
# - Returns status confirmations and logs details.

from neo4j import AsyncGraphDatabase
import json

class KnowledgeGraphUploader:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def upload_data(self, data: dict, state):
        # Prepare the Cypher query
        cypher_query = """
        // Create the Article node with text
        MERGE (article:Article {title: $jsonData.Article.Title})
        SET article.url = $jsonData.Article.URL,
            article.date_published = $jsonData.Article["Date Published"],
            article.text = $jsonData.Article.Text
        WITH article

        // Create Stakeholders and their relationships
        UNWIND $jsonData.Stakeholders AS stakeholderData
        MERGE (stakeholder:Stakeholder {name: stakeholderData.Name})
        SET stakeholder.type = stakeholderData.Type
        MERGE (stakeholder)-[:MENTIONED_IN]->(article)

        // Stakeholder Relationships
        FOREACH (_ IN CASE WHEN stakeholderData.Relationships.is_author IS NOT NULL THEN [1] ELSE [] END |
            MERGE (stakeholder)-[:IS_AUTHOR]->(article)
        )
        FOREACH (_ IN CASE WHEN stakeholderData.Relationships.is_employed_by IS NOT NULL THEN [1] ELSE [] END |
            MERGE (employer:Organization {name: stakeholderData.Relationships.is_employed_by})
            MERGE (stakeholder)-[:IS_EMPLOYED_BY]->(employer)
        )
        FOREACH (_ IN CASE WHEN stakeholderData.Relationships.has_role_in IS NOT NULL THEN [1] ELSE [] END |
            MERGE (institution:Institution {name: stakeholderData.Relationships.has_role_in})
            MERGE (stakeholder)-[r:HAS_ROLE_IN]->(institution)
            SET r.has_role = stakeholderData.Relationships.has_role
        )
        FOREACH (eventTitle IN stakeholderData.Relationships.participated_in |
            MERGE (event:Event {title: eventTitle})
            MERGE (stakeholder)-[:PARTICIPATED_IN]->(event)
        )
        FOREACH (_ IN CASE WHEN stakeholderData.Relationships.related_to IS NOT NULL THEN [1] ELSE [] END |
            MERGE (controversy:Controversy {summary: stakeholderData.Relationships.related_to})
            MERGE (stakeholder)-[:RELATED_TO]->(controversy)
        )
        WITH article, stakeholderData, stakeholder

        // Create Quotes
        UNWIND stakeholderData.Quotes AS quoteData
        MERGE (quote:Quote {text: quoteData.Text})
        SET quote.date_recorded = quoteData["Date Recorded"],
            quote.context = quoteData.Context
        MERGE (stakeholder)-[:SAID]->(quote)
        MERGE (quote)-[:MENTIONED_IN]->(article)
        WITH article

        // Create Events
        UNWIND $jsonData.Events AS eventData
        MERGE (event:Event {title: eventData.Title})
        SET event.date = eventData.Date,
            event.description = eventData.Description
        MERGE (event)-[:MENTIONED_IN]->(article)
        FOREACH (participantName IN eventData.Participants |
            MERGE (participant:Stakeholder {name: participantName})
            MERGE (participant)-[:PARTICIPATED_IN]->(event)
        )
        WITH article

        // Create Facts
        UNWIND $jsonData.Facts AS factData
        MERGE (fact:Fact {fact: factData.Fact})
        SET fact.summary = factData.Summary,
            fact.description = factData.Description
        MERGE (article)-[:CITES]->(fact)
        WITH article

        // Create Issues
        UNWIND $jsonData.Issues AS issueData
        MERGE (issue:Issue {title: issueData.Title})
        SET issue.objective = issueData.Objective
        MERGE (article)-[:IS_ABOUT]->(issue)
        WITH article

        // Create Documents
        UNWIND $jsonData.Documents AS documentData
        MERGE (document:Document {title: documentData["Document Title"]})
        SET document.description = documentData.Description
        MERGE (article)-[:MENTIONS]->(document)
        WITH article

        // Create Controversies
        UNWIND $jsonData.Controversies AS controversyData
        MERGE (controversy:Controversy {summary: controversyData.Summary})
        SET controversy.description = controversyData.Description,
            controversy.controversy_type = controversyData["Controversy Type"]
        MERGE (article)-[:MENTIONS]->(controversy)
        WITH article

        // Create Institutions
        UNWIND $jsonData.Institutions AS institutionData
        MERGE (institution:Institution {name: institutionData.Name})
        SET institution.type = institutionData.Type
        MERGE (article)-[:MENTIONS]->(institution)
        """

        # Execute the Cypher query
        try:
            async with self.driver.session() as session:
                result = await session.write_transaction(
                    self._run_query, cypher_query, data
                )
                return True, f"Data from article '{data['Article']['Title']}' has been merged into the knowledge graph."
        except Exception as e:
            return False, str(e)

    @staticmethod
    async def _run_query(tx, query, json_data):
        await tx.run(query, jsonData=json_data)
