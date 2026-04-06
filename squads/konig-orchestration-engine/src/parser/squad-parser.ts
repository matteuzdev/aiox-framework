import { readFileSync, existsSync, readdirSync } from 'fs'
import { join, dirname } from 'path'
import { parse as parseYaml } from 'yaml'
import matter from 'gray-matter'
import type { SquadManifest, TaskDefinition, AgentDefinition, WorkflowDefinition } from '../types/index.js'

export class SquadParser {
  private squadsRoot: string

  constructor(squadsRoot: string) {
    this.squadsRoot = squadsRoot
  }

  parseSquadManifest(squadName: string): SquadManifest {
    const manifestPath = join(this.squadsRoot, squadName, 'squad.yaml')
    if (!existsSync(manifestPath)) {
      throw new Error(`Squad manifest not found: ${manifestPath}`)
    }
    const content = readFileSync(manifestPath, 'utf-8')
    return parseYaml(content) as SquadManifest
  }

  listAllSquads(): string[] {
    if (!existsSync(this.squadsRoot)) return []
    return readdirSync(this.squadsRoot, { withFileTypes: true })
      .filter(dirent => dirent.isDirectory() && !dirent.name.startsWith('.') && dirent.name !== 'pixel-agents' && !dirent.name.endsWith('-engine'))
      .map(dirent => dirent.name)
  }

  parseTask(squadName: string, taskFile: string): TaskDefinition {
    const taskPath = join(this.squadsRoot, squadName, 'tasks', taskFile)
    if (!existsSync(taskPath)) {
      throw new Error(`Task file not found: ${taskPath}`)
    }
    const content = readFileSync(taskPath, 'utf-8')
    const parsed = matter(content)
    const frontmatter = parsed.data as Omit<TaskDefinition, 'command'>

    const commandMatch = parsed.content.match(/^#\s+\*(.+)$/m)
    const command = commandMatch ? commandMatch[1] : taskFile.replace('.md', '')

    return {
      ...frontmatter,
      command,
    }
  }

  parseAgent(squadName: string, agentFile: string): AgentDefinition {
    const agentPath = join(this.squadsRoot, squadName, 'agents', agentFile)
    if (!existsSync(agentPath)) {
      throw new Error(`Agent file not found: ${agentPath}`)
    }
    const content = readFileSync(agentPath, 'utf-8')
    const yamlMatch = content.match(/```yaml\n([\s\S]*?)\n```/)
    if (!yamlMatch) {
      throw new Error(`No YAML block found in agent file: ${agentFile}`)
    }
    return parseYaml(yamlMatch[1]) as AgentDefinition
  }

  parseWorkflow(squadName: string, workflowFile: string): WorkflowDefinition {
    const workflowPath = join(this.squadsRoot, squadName, 'workflows', workflowFile)
    if (!existsSync(workflowPath)) {
      throw new Error(`Workflow file not found: ${workflowPath}`)
    }
    const content = readFileSync(workflowPath, 'utf-8')
    const steps: string[] = []
    const stepMatches = content.matchAll(/\d+\.\s+`([^`]+)`/g)
    for (const match of stepMatches) {
      steps.push(match[1])
    }
    const nameMatch = content.match(/^#\s+(.+)$/m)
    return {
      name: nameMatch ? nameMatch[1] : workflowFile.replace('.md', ''),
      description: '',
      steps,
    }
  }

  parseSquadFull(squadName: string) {
    const manifest = this.parseSquadManifest(squadName)
    const tasks = manifest.components.tasks.map(t => this.parseTask(squadName, t))
    const agents = manifest.components.agents.map(a => this.parseAgent(squadName, a))
    const workflows = manifest.components.workflows.map(w => this.parseWorkflow(squadName, w))

    return { manifest, tasks, agents, workflows }
  }
}
