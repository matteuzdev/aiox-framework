import { existsSync, mkdirSync, writeFileSync, readFileSync, readdirSync } from 'fs'
import { join } from 'path'
import type { RunState, TaskRunState, HandoffContract } from '../types/index.js'

export class RunStore {
  private runsDir: string

  constructor(runsDir: string) {
    this.runsDir = runsDir
    if (!existsSync(runsDir)) {
      mkdirSync(runsDir, { recursive: true })
    }
  }

  createRun(squad: string, workflow?: string): RunState {
    const runId = this.generateRunId(squad)
    const runState: RunState = {
      id: runId,
      squad,
      workflow,
      tasks: [],
      status: 'pending',
      startedAt: new Date().toISOString(),
      artifacts: {},
    }
    this.saveRun(runState)
    return runState
  }

  saveRun(runState: RunState): void {
    const runDir = join(this.runsDir, runState.squad, runState.id)
    if (!existsSync(runDir)) {
      mkdirSync(runDir, { recursive: true })
    }
    writeFileSync(join(runDir, 'run-state.json'), JSON.stringify(runState, null, 2))
  }

  loadRun(squad: string, runId: string): RunState | null {
    const runPath = join(this.runsDir, squad, runId, 'run-state.json')
    if (!existsSync(runPath)) return null
    return JSON.parse(readFileSync(runPath, 'utf-8')) as RunState
  }

  listRuns(squad: string): RunState[] {
    const squadDir = join(this.runsDir, squad)
    if (!existsSync(squadDir)) return []
    return readdirSync(squadDir)
      .filter(d => existsSync(join(squadDir, d, 'run-state.json')))
      .map(d => JSON.parse(readFileSync(join(squadDir, d, 'run-state.json'), 'utf-8')) as RunState)
  }

  addTask(runState: RunState, task: TaskRunState): void {
    runState.tasks.push(task)
    this.saveRun(runState)
  }

  updateTask(runState: RunState, taskName: string, updates: Partial<TaskRunState>): void {
    const task = runState.tasks.find(t => t.task === taskName)
    if (!task) throw new Error(`Task not found in run: ${taskName}`)
    Object.assign(task, updates)
    this.saveRun(runState)
  }

  addArtifact(runState: RunState, name: string, content: string, path: string): void {
    runState.artifacts[name] = path
    const runDir = join(this.runsDir, runState.squad, runState.id)
    writeFileSync(join(runDir, name), content)
    this.saveRun(runState)
  }

  addHandoffLog(runState: RunState, handoff: HandoffContract): void {
    const runDir = join(this.runsDir, runState.squad, runState.id)
    const logPath = join(runDir, 'handoff-log.md')
    const existing = existsSync(logPath) ? readFileSync(logPath, 'utf-8') : `# Handoff Log - Run ${runState.id}\n\n`
    const entry = `## ${handoff.from} -> ${handoff.to}\n\n` +
      `[HANDOFF]\n` +
      `de: ${handoff.from}\n` +
      `para: ${handoff.to}\n` +
      `objetivo: ${handoff.objective}\n` +
      `artefatos: ${handoff.artefatos.join(', ')}\n` +
      `criterio_de_aceite: ${handoff.criterio_de_aceite}\n` +
      `status: ${handoff.status}\n` +
      `[/HANDOFF]\n\n`
    writeFileSync(logPath, existing + entry)
  }

  private generateRunId(squad: string): string {
    const date = new Date().toISOString().split('T')[0]
    const squadDir = join(this.runsDir, squad)
    const count = existsSync(squadDir) ? readdirSync(squadDir).length + 1 : 1
    return `${date}-run-${String(count).padStart(3, '0')}`
  }
}
