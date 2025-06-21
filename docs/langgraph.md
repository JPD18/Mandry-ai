I am building a LangGraph server for a visa assistant application. I’ve designed a basic workflow diagram and now I want to implement it as a LangGraph using Python, with proper integration into my database.

Workflow Summary:
Start → goes to load_profile

load_profile:

If the profile is empty → go to ask_record_update

If the profile is full → go to qna

ask_record_update:

Collect and update user data

If still not enough info → repeat this node

If enough info is collected → proceed to qna

qna:

Conduct Q&A session based on visa type

When done, move to end

end: Finish interaction

Requirements:
Implement each node as a LangGraph-compatible function.

Use my database (e.g., PostgreSQL via SQLAlchemy, or my repo’s custom ORM) to load and update user profiles.

Use LangChain agents or tools where needed.

Clearly define edges/transitions between nodes.

Add fallback logic in ask_record_update if information remains insufficient.

Output:
Provide the LangGraph definition (with edges).

Implement node functions: load_profile, ask_record_update, qna, end.

Use dummy DB logic if needed, but keep it structured so I can plug in real database code.

Include comments to clarify each step.use The @/backend is a @Django server. Incorporate the langgraph into the main page for the qna, and make sure when we are asking about the user we have indication in the frontend that we are asking for the profile, and then, when profile is loaded add, make sure we switch for the qna

## Second iteration
great, but I think there was not enought clarify on what I count as  a user profile, It has to contain some strucutred and unstructured data. No passport number and some other info. The goal of the user profile is to give agent a context of what user is searching for: for example, you say I am ukrainian and I wan to apply for visas, then llm knowing this, needs to figure out, what other info it might need about the user for example their marital status, or rough age, or education or plans. Since the profile is going to be different from person to person it has to have quite a log of freedom, so let's work around that idea.