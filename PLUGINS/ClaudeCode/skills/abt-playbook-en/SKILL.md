---
name: ABT-playbook-en
description: 'Operate ABT playbook definitions and playbook run records. Use when users want to list runnable definitions, execute playbooks, or inspect run history.'
argument-hint: 'list playbook definitions | run playbook <name> for <target_type> <target_id> | list playbook runs [filters]'
compatibility: connect to ABT mcp server
metadata:
  author: Funnywolf
  version: 0.1.0
  mcp-server: ABT
  category: cyber security
  tags: [ playbook, automation, soar, investigation ]
  documentation: https://ABT.viperrtp.com/
---

# ABT Playbook

Use this skill when the user needs to work with playbook automation on ABT.

## When to Use

- The user wants to know which playbook definitions are currently available to run.
- The user wants to run a playbook against a case, alert, or artifact.
- The user wants to inspect playbook run records by target object, type, or job status.
- The user wants to confirm whether a target object has already been automated.

## Operating Rules

- Keep playbook definitions and playbook run records strictly separate in language and workflow.
- Use `list_available_playbook_definitions` only for runnable definitions.
- Use `list_playbook_runs` only for run records.
- Use `execute_playbook` only when the user has named a runnable definition and identified the target object.
- Do not invent a playbook definition name. If it is missing, list or suggest available definitions first.
- Treat `user_input` as optional natural-language guidance for that specific run, not as a generic chat prompt.

## Decision Flow

1. If the user wants to know what can run, call `list_available_playbook_definitions`.
2. If the user wants to confirm whether automation has run for a case, alert, or artifact, call `list_playbook_runs(source_id=<target_id>, type=[<target_type>])`.
3. If the user wants to run automation and already provides the definition name plus target object, call `execute_playbook`.
4. If the user wants to run automation but does not know the definition name, call `list_available_playbook_definitions` first.
5. If the user wants the overall automation history, call `list_playbook_runs` with the narrowest useful filters.

## SOP

### List Runnable Playbook Definitions

1. Call `list_available_playbook_definitions`.
2. Parse the returned JSON.
3. Show only the definitions that are most relevant to the user's target object or goal.
4. Make it explicit that these are definitions, not run records.

### Run a Playbook

1. Require `target_type`, `target_id`, and the playbook definition `name`.
2. If the definition name is missing or uncertain, call `list_available_playbook_definitions` first.
3. Pass `user_input` only when the user wants extra guidance for that run.
4. Call `execute_playbook(type=<target_type>, record_id=<target_id>, name=<definition_name>, user_input=<optional>)`.
5. Confirm that a pending playbook run record was created.

Preferred response structure:

- `Target`: type and ID
- `Playbook Definition`: selected name
- `Run Status`: pending at creation time unless the platform reports otherwise
- `User Input`: only if provided
- `Next Useful Step`: usually to query related playbook runs

### Review Playbook Runs

1. Extract supported filters: `playbook_id`, `job_status`, `type`, `source_id`, and `limit`.
2. Use `source_id` when the user is asking from the perspective of one case, alert, or artifact.
3. Call `list_playbook_runs`.
4. Parse the returned JSON strings.
5. Present a short run-oriented view.

Preferred response structure:

| Run ID | Type | Target ID | Job Status | Definition Name | Updated |
|--------|------|-----------|------------|-----------------|---------|

Then add one short interpretation line when useful.

## Clarification Rules

- Ask for `target_type` and `target_id` only when they are missing for run requests.
- Ask for the playbook definition name only when it is missing or ambiguous.
- If the user names something that sounds like a run ID instead of a definition, clarify before executing.
- If the user asks to "check the run" without a run ID, prefer `list_playbook_runs` with object context instead of guessing a specific run.

## Output Rules

- Be concise.
- Do not blur the words definition, run, record, and target object.
- Do not dump all playbook definitions if only a shortlist is relevant.
- Prefer operational wording: what can run, what ran, what is pending, and what should be checked next.

## Failure Handling

- If no matching playbook definitions exist, say that directly and suggest the closest relevant options.
- If no run records exist for the target, say that directly.
- If execution prerequisites are missing, ask one focused clarification instead of guessing.
- If the user asks for something only run records can answer, do not answer from definitions alone.