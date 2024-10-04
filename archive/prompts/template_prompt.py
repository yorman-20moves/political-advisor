from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate


# Another Agent Prompts (Example)
# -------------------------------

ANOTHER_AGENT_SYSTEM_PROMPT = """[Your system prompt for another agent]"""

ANOTHER_AGENT_HUMAN_PROMPT = """[Your human prompt for another agent]"""

ANOTHER_AGENT_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(ANOTHER_AGENT_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template(ANOTHER_AGENT_HUMAN_PROMPT)
])
