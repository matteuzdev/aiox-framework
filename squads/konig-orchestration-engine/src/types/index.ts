export interface SquadManifest {
  name: string
  version: string
  description: string
  author: string
  license: string
  slashPrefix: string
  aiox: {
    minVersion: string
    type: string
  }
  components: {
    tasks: string[]
    agents: string[]
    workflows: string[]
    checklists: string[]
    templates: string[]
    tools: string[]
    scripts: string[]
  }
  config: {
    extends: string
    'coding-standards': string
    'tech-stack': string
    'source-tree': string
  }
  dependencies: {
    node: string[]
    python: string[]
    squads: string[]
  }
  tags: string[]
}

export interface TaskDefinition {
  task: string
  responsavel: string
  responsavel_type: string
  atomic_layer: string
  Entrada: string
  Saida: string
  Checklist: string[]
  command: string
}

export interface AgentDefinition {
  agent: {
    name: string
    id: string
    title: string
    icon: string
    whenToUse: string
  }
  persona: {
    role: string
    style: string
    focus: string
  }
  commands: Array<{
    name: string
    description: string
    task: string
  }>
}

export interface HandoffContract {
  id: string
  from: string
  to: string
  objective: string
  artefatos: string[]
  criterio_de_aceite: string
  status: 'ready' | 'blocked' | 'completed' | 'failed'
  timestamp: string
  runId: string
}

export interface RunState {
  id: string
  squad: string
  workflow?: string
  tasks: TaskRunState[]
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused'
  startedAt: string
  completedAt?: string
  artifacts: Record<string, string>
}

export interface TaskRunState {
  task: string
  agent: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  inputs: Record<string, unknown>
  outputs: Record<string, string>
  checklistResult?: {
    passed: boolean
    details: string[]
  }
  startedAt?: string
  completedAt?: string
  error?: string
}

export interface WorkflowDefinition {
  name: string
  description: string
  steps: string[]
}

export interface AgentLaunchConfig {
  agentId: string
  taskDefinition: TaskDefinition
  inputs: Record<string, unknown>
  artifacts: Record<string, string>
  mode: 'codex-cli' | 'claude-api'
  cwd: string
  runId: string
}
