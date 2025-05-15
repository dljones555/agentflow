# Sample SEC doc analysis tool of today: https://github.com/vishukla/agentvest/blob/main/agents/sec_filings_agent.py
# - uses standard tooling of today.
#
# Another option with maturity relative today:
# https://docs.oap.langchain.com/ - langchain openagent platform and langraph, lots of traction
#
# But future looks more "democratized": think Excel macros, Tableau, apier
# - Best of visual
# - Best of DSL
# - Generative
# - New/future looking paradigms
# - Low/no-code
# - Not as py centric
# - Accounts for compute/energy, scaling, deployment, goal monitoring, price
# - Allows for re-training, new evals and updates based on HTIL
# - Auto gen/re-run evals based on sampling of agent interactions and retraining
#
# CSR goals and metrics: net promoter score, dropoff rates, re-engage time, escalation, 
# Prompt Loader: Load prompts from Weaviate

prompt_loader classify_prompts:
    source: "weaviate://prompt-index"
    query: "prompts for classify"

prompt_loader extract_prompts:
    source: "weaviate://prompt-index"
    query: "prompts for extract"

prompt_loader feedback_prompts:
    source: "weaviate://prompt-index"
    query: "prompts for update_examples"

# Memory: Short-term session context
memory session_context:
    type: short_term
    store: "redis://cache" for "company_{{company_id}}"
    retrieve: "recent_filings for {{company_id}}"

# Memory: Long-term example storage
memory example_storage:
    type: long_term
    store: "weaviate://examples-index" for "examples_{{filing_id}}"
    retrieve: "examples for {{filing_id}}"

# MCP: Financial database integration
mcp db_update:
    endpoint: "https://finance.api/filings"
    payload:
        filing_id: string
        health: string
        details: dict
    response:
        success: boolean
        message: string

# Intent: Analyze SEC filings
intent analyze_filings:
    goal: "Classify filings as strong, stable, or weak to assess financial health"
    metric: accuracy "Classification accuracy above 90%"
    source: "weaviate://sec-index"
    events: "filing_uploaded, daily_batch_triggered"
    strategy: "extract_then_classify"

# Resource: Fetch filing context
get filing_context(filing_id, company_id):
    search: "weaviate://sec-index" for "data on {{filing_id}}" top 5
    load: "gs://firm-bucket/sec/{{filing_id}}.pdf"
    memory.session_context: retrieve "recent_filings for {{company_id}}"

# Prompt: Extract financial data
ask ai.extract(filing, context, session_context):
    guide: "Extract company name, revenue, debt, risks from SEC filing"
    examples:
        "Apple 10-K, $394B revenue, $120B debt, supply chain risk" -> 
            {"name": "Apple", "revenue": 394000000000, "debt": 120000000000, "risks": ["supply chain"]}
        "SmallCo 10-K, $1B revenue, $2B debt, regulatory risk" -> 
            {"name": "SmallCo", "revenue": 1000000000, "debt": 2000000000, "risks": ["regulatory"]}  # HITL-updated
    loader: prompt_loader.extract_prompts
    gives: details (dict)

# Prompt: Classify financial health
ask ai.classify(details, session_context):
    guide: "Classify financial health as strong, stable, or weak based on revenue and debt"
    examples:
        {"revenue": 394000000000, "debt": 120000000000} -> "strong"
        {"revenue": 1000000000, "debt": 2000000000} -> "weak"  # HITL-updated
    loader: prompt_loader.classify_prompts
    gives: health (string)

# Prompt: Incorporate HITL feedback
ask ai.update_examples(feedback, filing, details, health):
    guide: "Update examples for extract and classify based on human feedback"
    examples:
        {"feedback": "Correct health to weak", "filing": "SmallCo 10-K"} -> 
            {"extract": {"input": "SmallCo 10-K", "output": {"name": "SmallCo", "revenue": 1000000000, "debt": 2000000000, "risks": ["regulatory"]}}, 
             "classify": {"input": {"revenue": 1000000000, "debt": 2000000000}, "output": "weak"}}
    loader: prompt_loader.feedback_prompts
    gives: updated_examples (dict)

# A2A: Escalate to Risk Analyst agent
a2a escalate:
    target: agent.RiskAnalyst
    input:
        filing_id: string
        health: string
        details: dict
    output:
        analyst_response: string

# Flow: Process filing
flow process_filing(filing_id, company_id):
    get filing_context(filing_id, company_id)
    details = ask.ai.extract(filing_id, filing_context, session_context)
    health = ask.ai.classify(details, session_context)
    store: "weaviate://sec-index" data {"id": filing_id, "details": details, "health": health}
    mcp.db_update:
        filing_id: filing_id
        health: health
        details: details
    if health is "weak":
        analyst_response = a2a.escalate(filing_id, health, details)
        warn: "Warning: {{details.name}} has weak financials, debt {{details.debt}}: {{analyst_response}}"
    else:
        say: "{{details.name}} classified as {{health}}"
    # HITL feedback
    feedback = ui.get_feedback(filing_id, details, health)
    if feedback:
        updated_examples = ask.ai.update_examples(feedback, filing_id, details, health)
        memory.example_storage: store "examples_{{filing_id}}" data updated_examples
    gives: response (string)

# Agent: SEC processor
agent SECProcessor:
    use intent.analyze_filings

# Agent: Risk Analyst for escalations
agent RiskAnalyst:
    use flow.handle_escalation

# Flow: Handle escalation
flow handle_escalation(filing_id, health, details):
    say: "Escalated filing {{filing_id}}: {{health}}, review risks {{details.risks}}"
    gives: analyst_response (string)

# Workflow: Batch process filings
workflow batch_analyze(filing_ids, company_id):
    parallel:
        responses = for id in filing_ids: agent.SECProcessor(id, company_id)
    gives:
        responses: responses

# UI: Web dashboard
ui sec_dashboard:
    type: screen
    render: workflow.batch_analyze
    input: filing_ids (list), company_id (string)
    output: responses
    feedback: details, health
