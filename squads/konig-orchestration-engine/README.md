# Konig Orchestration Engine

Execution engine for Konig Systems - transforms agent definitions into executable workflows.

## What This Does

This is the **operating system** for your company of agents. It reads your squad definitions, task files, and agent personas, then executes them autonomously with proper handoffs, artifact routing, and validation.

## Architecture

```
src/
  parser/
    squad-parser.ts       # Reads squad.yaml, tasks/*.md, agents/*.md
  orchestrator/
    task-runner.ts        # Executes tasks and workflows in sequence
  launcher/
    agent-launcher.ts     # Launches agents via Codex CLI or Claude API
  router/
    handoff-manager.ts    # Manages inter-squad handoff contracts
    checklist-validator.ts # Validates task outputs against checklists
  state/
    run-store.ts          # Persists run state and artifacts
  cli/
    commands.ts           # CLI: konig list, run, status, route
```

## CLI Commands

```bash
# List all squads
konig list squads

# List tasks for a squad
konig list tasks --squad konig-instagram-intelligence-core

# List agents for a squad
konig list agents --squad konig-athenaeum-core

# Run a single task
konig run task analyze-instagram-competition.md --squad konig-instagram-intelligence-core --input '{"niche":"oftalmo"}'

# Run a full workflow
konig run workflow athenaeum-cycle.md --squad konig-athenaeum-core

# Route work through squads
konig route "Create Instagram content for ophthalmology clinic" --urgency high

# Check run status
konig status --squad konig-instagram-intelligence-core
konig status --squad konig-instagram-intelligence-core --run 2026-04-04-run-001
```

## Execution Modes

- **codex-cli** (default): Uses Codex CLI to launch agents as subprocesses
- **claude-api**: Uses Claude API directly (requires `ANTHROPIC_API_KEY`)

## How It Works

1. **Parse**: Reads `squad.yaml` to discover tasks, agents, and workflows
2. **Resolve**: Maps `responsavel: @agent-id` to actual agent definitions
3. **Build Prompt**: Combines agent persona + task definition + inputs + artifacts
4. **Launch**: Executes agent via CLI or API
5. **Collect**: Saves outputs to `runs/<squad>/<run-id>/`
6. **Validate**: Runs checklist validation against outputs
7. **Handoff**: Passes artifacts to next task in workflow, logs handoff protocol

## Handoff Protocol

Automatic handoff generation between tasks:

```
[HANDOFF]
de: competitor-intel-analyst
para: content-pattern-strategist
objetivo: Transform competitive analysis into editorial pillars
artefatos: competitor_map.md, viral_patterns.md, content_gaps.md
criterio_de_aceite: editorial_war_map.md and post_backlog.md delivered
status: ready
[/HANDOFF]
```

## Run State

All execution state is persisted:

```
runs/
  konig-instagram-intelligence-core/
    2026-04-04-run-001/
      run-state.json        # Full run state with task statuses
      handoff-log.md        # Handoff protocol log
      competitor_map.md     # Task output artifacts
      viral_patterns.md
      content_gaps.md
      ...
```

## Setup

```bash
npm install
npm run build
npm link  # Makes `konig` available globally
```

## Next Steps

- [ ] Test with Instagram pipeline as proof of concept
- [ ] Add parallel task execution for independent tasks
- [ ] Add retry and error recovery logic
- [ ] Add webhook triggers for external events
- [ ] Integrate with pixel-agents for visual monitoring
