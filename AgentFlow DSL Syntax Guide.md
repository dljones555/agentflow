# AgentFlow DSL Syntax Guide

## Overview
AgentFlow is a Python-like, non-developer-friendly DSL for creating AI agents. It uses simple syntax to define prompts, flows, resources, agents, workflows, error handling, and evaluations. It integrates with LLMs (PyTorch), RAG, vector DBs (Weaviate), and cloud platforms (GCP/Azure), with Rust/Go/.NET for efficiency and MCP-compliant APIs for interoperability.

## Design Principles
- **Concise**: Minimal, Python-like syntax (e.g., `ask.ai.classify(input)`).
- **Readable**: English-like verbs (e.g., `say`, `if`, `get`).
- **Non-Dev**: Intuitive for managers, no coding required.
- **Scalable**: Handles thousands of agents via cloud.
- **Energy-Adaptable**: Rust for edge, PyTorch/XLA for cloud.
- **UI-Ready**: Auto-generates UIs (web, voice, edge) via Vercel/v0/Power Apps.

## Syntax Structure

### 1. Prompt Definition
Defines an AI task, like classifying or summarizing.

- **Syntax**:
  ```
  ask ai.<name>(<input>, [<context>]):
      guide: "<system instruction>"
      examples:
          "<input>" -> "<output>"
          ...
      gives: <output> (<type>)
  ```
- **Nouns**: Prompt, Guide, Example, Input, Output, Context
- **Verbs**: Ask, Classify, Summarize, Extract
- **Notes**:
  - `<name>`: Task name (e.g., `classify`, `summarize`).
  - `<input>`: Primary input (e.g., string, dict).
  - `<context>`: Optional RAG context.
  - `<type>`: Output type (e.g., string, dict, float).

### 2. Flow Block
Defines logic for agent tasks, like processing inputs.

- **Syntax**:
  ```
  flow <name>(<input>):
      <variable> = <action>
      if <condition>:
          <action>
      elif <condition>:
          <action>
      else:
          <action>
      gives: <output> (<type>)
  ```
- **Nouns**: Flow, Variable, Condition, Output
- **Verbs**: If, Elif, Else, Say, Store, Return
- **Notes**:
  - `<action>`: Calls like `ask.ai.<name>`, `say "<message>"`, or `store`.
  - `<condition>`: Boolean (e.g., `type is "refund"`).
  - Supports loops with `for <var> in <list>`.

### 3. Resource Call
Fetches context for prompts, like RAG or files.

- **Syntax**:
  ```
  get <name>(<input>):
      search: "<db>" for "<query>" top <n>
      fetch: "<url>"
      load: "<file_path>"
  ```
- **Nouns**: Resource, Context, Database, URL, File
- **Verbs**: Get, Search, Fetch, Load
- **Notes**:
  - `<db>`: Vector DB (e.g., `weaviate://index`).
  - `<query>`: Search string with `{{input}}`.
  - `<file_path>`: Cloud storage (e.g., `gs://bucket/file`).

### 4. Agent Definition
Creates an agent to run a flow.

- **Syntax**:
  ```
  agent <name>:
      use flow.<name>
  ```
- **Nouns**: Agent, Flow
- **Verbs**: Use
- **Notes**:
  - Links agent to a single flow for execution.

### 5. Workflow Block
Coordinates multiple tasks or agents, with parallel/serial execution.

- **Syntax**:
  ```
  workflow <name>(<inputs>):
      get <resource>(<input>)
      do:
          <variable> = <agent|flow|ask>.<name>(<input>)
          ...
      parallel:
          <variable> = <agent|flow|ask>.<name>(<input>)
          ...
      gives:
          <key>: <variable>
          ...
  ```
- **Nouns**: Workflow, Input, Output, Variable
- **Verbs**: Do, Parallel, Get, Gives
- **Notes**:
  - `do`: Sequential tasks.
  - `parallel`: Concurrent tasks.
  - `<inputs>`: Multiple inputs (e.g., `question, item`).

### 6. Error Handling
Catches and handles errors during execution.

- **Syntax**:
  ```
  flow <name>(<input>):
      try:
          <action>
      catch:
          <action>
      gives: <output> (<type>)
  ```
- **Nouns**: Error, Output
- **Verbs**: Try, Catch, Say
- **Notes**:
  - `<action>` in `catch`: Usually `say "<error message>"`.

### 7. Evaluation Block
Tests agent performance with metrics.

- **Syntax**:
  ```
  eval <name>:
      test: "<data_path>"
      score: <metric>
          match: <action> with <expected>
      gives: <output> (<type>)
  ```
- **Nouns**: Dataset, Metric, Score, Output
- **Verbs**: Test, Score, Match, Gives
- **Notes**:
  - `<data_path>`: Cloud storage (e.g., `azure://bucket/data.csv`).
  - `<metric>`: E.g., `accuracy`, `f1`.

### 8. UI Integration
Auto-generates interfaces for agent interaction.

- **Syntax**:
  ```
  ui <name>:
      type: <screen|voice|edge>
      render: <workflow|flow>
      input: <fields>
      output: <fields>
  ```
- **Nouns**: Interface, Type, Input, Output
- **Verbs**: Render, Interact
- **Notes**:
  - `<type>`: Interface type (e.g., `screen` for web, `edge` for devices).
  - `<fields>`: Input/output fields (e.g., `doc_id`, `response`).
  - Auto-generates UIs via v0-like AI or Streamlit/Power Apps templates.

## Integration Details
- **LLMs**: PyTorch on GCP Vertex AI/Azure ML for `ask.ai` prompts.
- **RAG/Vector DBs**: Weaviate/Qdrant for `get` searches, hosted on GKE/AKS.
- **Cloud**: GCP Cloud Run/Azure Functions for scalability.
- **Efficiency**: Rust for edge UIs (e.g., retail kiosks), Go/.NET for cloud APIs.
- **MCP**: APIs for context passing:
  ```
  POST /mcp/run
  Input: {"workflow": "<name>", "input": {...}, "context": {...}}
  Output: {"output": {...}, "context": {...}}
  ```
- **UI Scaffolding**:
  - Web: Vercel-hosted React, generated by v0-like AI.
  - Voice: GCP Speech-to-Text for commands.
  - Edge: Rust-generated HTML for low-power devices.

## Reserved Keywords
- Verbs: `ask`, `get`, `if`, `elif`, `else`, `for`, `try`, `catch`, `say`, `store`, `do`, `parallel`, `use`, `test`, `score`, `match`, `render`
- Nouns: `ai`, `flow`, `agent`, `workflow`, `eval`, `ui`, `guide`, `examples`, `gives`, `search`, `fetch`, `load`, `type`, `input`, `output`

## Notes
- **Non-Dev Focus**: Syntax mimics flow editor (e.g., “if condition, do action”).
- **Scalability**: Workflows support parallel execution, cloud autoscaling.
- **Energy**: Rust for edge, PyTorch/XLA for cloud, serverless for idle efficiency.
- **UI**: Auto-generated via Streamlit/v0 for web, Power Apps for forms, Rust for edge.
