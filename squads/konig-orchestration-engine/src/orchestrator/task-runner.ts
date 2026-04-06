import { SquadParser } from '../parser/squad-parser.js'
import { AgentLauncher } from '../launcher/agent-launcher.js'
import { RunStore } from '../state/run-store.js'
import { ChecklistValidator } from '../router/checklist-validator.js'
import { HandoffManager } from '../router/handoff-manager.js'
import { NotionReporter } from '../notifier/notion-reporter.js'
import { readFileSync, readdirSync, statSync, copyFileSync, mkdirSync, existsSync } from 'fs'
import { join } from 'path'
import type { TaskRunState, HandoffContract } from '../types/index.js'

export class TaskRunner {
  private parser: SquadParser
  private launcher: AgentLauncher
  private runStore: RunStore
  private validator: ChecklistValidator
  private handoffManager: HandoffManager
  private notionReporter: NotionReporter

  constructor(squadsRoot: string, runsDir: string) {
    this.parser = new SquadParser(squadsRoot)
    this.launcher = new AgentLauncher()
    this.runStore = new RunStore(runsDir)
    this.validator = new ChecklistValidator()
    this.handoffManager = new HandoffManager()
    this.notionReporter = new NotionReporter()
  }

  async runTask(
    squadName: string,
    taskFile: string,
    inputs: Record<string, unknown> = {},
    artifacts: Record<string, string> = {},
    mode: 'codex-cli' | 'claude-api' = 'codex-cli',
  ): Promise<TaskRunState> {
    const task = this.parser.parseTask(squadName, taskFile)
    const agentId = task.responsavel.replace('@', '')

    const runState = this.runStore.createRun(squadName)

    const taskState: TaskRunState = {
      task: task.task,
      agent: agentId,
      status: 'running',
      inputs,
      outputs: {},
      startedAt: new Date().toISOString(),
    }
    this.runStore.addTask(runState, taskState)

    console.log(`[TASK] Running: ${task.task}`)
    console.log(`[TASK] Agent: ${agentId}`)
    console.log(`[TASK] Squad: ${squadName}`)

    try {
      const result = await this.launcher.launch({
        agentId,
        taskDefinition: task,
        inputs,
        artifacts,
        mode,
        cwd: this.getSquadDir(squadName),
        runId: runState.id,
      })

      taskState.outputs = { output: result.output }
      taskState.status = result.exitCode === 0 ? 'completed' : 'failed'
      taskState.completedAt = new Date().toISOString()

      if (result.exitCode !== 0) {
        taskState.error = result.output
      }

      if (result.exitCode === 0 && task.Checklist) {
        const validation = this.validator.validate(task.Checklist, this.getSquadDir(squadName))
        taskState.checklistResult = validation
        if (!validation.passed) {
          taskState.status = 'failed'
          taskState.error = `Checklist validation failed:\n${validation.details.join('\n')}`
        }
      }

      this.runStore.updateTask(runState, task.task, taskState)

      // Report to Notion
      const started = new Date(taskState.startedAt ?? new Date().toISOString())
      const ended = new Date(taskState.completedAt ?? Date.now())
      const durMs = ended.getTime() - started.getTime()
      const durMin = Math.floor(durMs / 60000)
      const durSec = Math.floor((durMs % 60000) / 1000)
      this.notionReporter.reportActivity({
        squad: squadName,
        task: task.task,
        agent: agentId,
        status: taskState.status as 'completed' | 'failed',
        runId: runState.id,
        duration: `${durMin}m ${durSec}s`,
        artifacts: 0,
        error: taskState.error,
      }).catch(() => {})

      console.log(`[TASK] Status: ${taskState.status}`)
      if (taskState.checklistResult) {
        console.log(`[TASK] Checklist: ${taskState.checklistResult.passed ? 'PASSED' : 'FAILED'}`)
      }

      return taskState
    } catch (error: unknown) {
      taskState.status = 'failed'
      taskState.error = String(error)
      taskState.completedAt = new Date().toISOString()
      this.runStore.updateTask(runState, task.task, taskState)

      // Report failure to Notion
      this.notionReporter.reportActivity({
        squad: squadName,
        task: task.task,
        agent: agentId,
        status: 'failed',
        runId: runState.id,
        error: String(error),
        artifacts: 0,
      }).catch(() => {})

      throw error
    }
  }

  async runWorkflow(
    squadName: string,
    workflowFile: string,
    initialInputs: Record<string, unknown> = {},
    mode: 'codex-cli' | 'claude-api' = 'codex-cli',
  ): Promise<void> {
    const squad = this.parser.parseSquadFull(squadName)
    const workflow = this.parser.parseWorkflow(squadName, workflowFile)

    console.log(`[WORKFLOW] Starting: ${workflow.name}`)
    console.log(`[WORKFLOW] Squad: ${squadName}`)
    console.log(`[WORKFLOW] Steps: ${workflow.steps.length}`)

    const runState = this.runStore.createRun(squadName, workflow.name)
    let accumulatedArtifacts: Record<string, string> = {}

    for (let i = 0; i < workflow.steps.length; i++) {
      const stepSlug = workflow.steps[i]
      const taskFile = this.findTaskBySlug(squad, stepSlug)

      if (!taskFile) {
        console.error(`[WORKFLOW] Task not found for slug: ${stepSlug}`)
        continue
      }

      const task = this.parser.parseTask(squadName, taskFile)
      const agentId = task.responsavel.replace('@', '')

      console.log(`\n[WORKFLOW] Step ${i + 1}/${workflow.steps.length}: ${stepSlug}`)
      console.log(`[WORKFLOW] Agent: ${agentId}`)

      const taskState: TaskRunState = {
        task: task.task,
        agent: agentId,
        status: 'running',
        inputs: i === 0 ? initialInputs : {},
        outputs: {},
        startedAt: new Date().toISOString(),
      }
      this.runStore.addTask(runState, taskState)

      try {
        const result = await this.launcher.launch({
          agentId,
          taskDefinition: task,
          inputs: i === 0 ? initialInputs : {},
          artifacts: accumulatedArtifacts,
          mode,
          cwd: this.getSquadDir(squadName),
          runId: runState.id,
        })

        taskState.outputs = { output: result.output }
        taskState.status = result.exitCode === 0 ? 'completed' : 'failed'
        taskState.completedAt = new Date().toISOString()

        if (result.exitCode !== 0) {
          taskState.error = result.output
          this.runStore.updateTask(runState, task.task, taskState)
          console.error(`[WORKFLOW] Step failed: ${stepSlug}`)
          break
        }

        if (task.Checklist) {
          const validation = this.validator.validate(task.Checklist, this.getSquadDir(squadName))
          taskState.checklistResult = validation
          if (!validation.passed) {
            taskState.status = 'failed'
            taskState.error = `Checklist failed: ${validation.details.join('\n')}`
            this.runStore.updateTask(runState, task.task, taskState)
            console.error(`[WORKFLOW] Checklist failed: ${stepSlug}`)
            break
          }
        }

        this.runStore.updateTask(runState, task.task, taskState)

        const squadDir = this.getSquadDir(squadName)
        const newFiles = this.detectNewFiles(squadDir, Object.values(accumulatedArtifacts))
        accumulatedArtifacts = { ...accumulatedArtifacts, ...newFiles }
        console.log(`[WORKFLOW] Step completed: ${stepSlug} (${Object.keys(newFiles).length} new artifacts)`)

        // Report individual task to Notion
        const started = new Date(taskState.startedAt ?? new Date().toISOString())
        const ended = new Date(taskState.completedAt ?? Date.now())
        const durMs = ended.getTime() - started.getTime()
        const durMin = Math.floor(durMs / 60000)
        const durSec = Math.floor((durMs % 60000) / 1000)
        this.notionReporter.reportActivity({
          squad: squadName,
          task: task.task,
          agent: agentId,
          status: taskState.status as 'completed' | 'failed',
          runId: runState.id,
          workflow: workflow.name,
          duration: `${durMin}m ${durSec}s`,
          artifacts: Object.keys(newFiles).length,
          error: taskState.error,
        }).catch(() => {})

        if (i < workflow.steps.length - 1) {
          const nextTaskFile = this.findTaskBySlug(squad, workflow.steps[i + 1])
          if (nextTaskFile) {
            const nextTask = this.parser.parseTask(squadName, nextTaskFile)
            const currentAgent = squad.agents.find(a => a.agent.id === agentId)
            const nextAgent = squad.agents.find(a => nextTask.responsavel.includes(a.agent.id))

            if (currentAgent && nextAgent) {
              const handoff = this.handoffManager.buildHandoff(
                currentAgent,
                nextAgent,
                task,
                nextTask,
                Object.keys(accumulatedArtifacts),
                runState.id,
              )
              this.runStore.addHandoffLog(runState, handoff)
              console.log(`[HANDOFF] ${handoff.from} -> ${handoff.to}`)
            }
          }
        }

      } catch (error: unknown) {
        taskState.status = 'failed'
        taskState.error = String(error)
        taskState.completedAt = new Date().toISOString()
        this.runStore.updateTask(runState, task.task, taskState)
        console.error(`[WORKFLOW] Error in step: ${stepSlug}`, error)
        break
      }
    }

    runState.status = runState.tasks.every(t => t.status === 'completed') ? 'completed' : 'failed'
    runState.completedAt = new Date().toISOString()
    this.runStore.saveRun(runState)

    // Report workflow completion to Notion
    const started = new Date(runState.tasks[0]?.startedAt ?? Date.now())
    const ended = new Date(runState.completedAt ?? Date.now())
    const durMs = ended.getTime() - started.getTime()
    const durMin = Math.floor(durMs / 60000)
    const durSec = Math.floor((durMs % 60000) / 1000)
    this.notionReporter.reportRunComplete(
      squadName,
      workflow.name,
      runState.id,
      runState.tasks.map(t => ({ task: t.task, agent: t.agent, status: t.status, error: t.error, outputs: t.outputs })),
      `${durMin}m ${durSec}s`,
    ).catch(() => {})

    console.log(`\n[WORKFLOW] Final status: ${runState.status}`)
  }

  private getSquadDir(squadName: string): string {
    return this.parser['squadsRoot'] + '/' + squadName
  }

  private findTaskBySlug(squad: ReturnType<SquadParser['parseSquadFull']>, slug: string): string | null {
    for (const task of squad.tasks) {
      if (task.command === slug) {
        return squad.manifest.components.tasks.find(t => t.replace('.md', '') === slug) || null
      }
    }
    return squad.manifest.components.tasks.find(t => t.replace('.md', '') === slug) || null
  }

  private detectNewFiles(squadDir: string, existingPaths: string[]): Record<string, string> {
    const artifacts: Record<string, string> = {}
    const existingSet = new Set(existingPaths)

    try {
      const files = readdirSync(squadDir)
      for (const file of files) {
        const fullPath = join(squadDir, file)
        if (existingSet.has(fullPath)) continue
        if (file.startsWith('.') || file.startsWith('_')) continue
        if (!file.endsWith('.md')) continue

        const stat = statSync(fullPath)
        if (!stat.isFile()) continue

        const age = Date.now() - stat.mtimeMs
        if (age > 600000) continue

        artifacts[file] = fullPath
      }
    } catch {
    }

    return artifacts
  }
}
