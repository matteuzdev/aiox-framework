import type { TaskDefinition, AgentDefinition, SquadManifest, HandoffContract } from '../types/index.js'

export class HandoffManager {
  buildHandoff(
    fromAgent: AgentDefinition,
    toAgent: AgentDefinition,
    fromTask: TaskDefinition,
    toTask: TaskDefinition,
    artifacts: string[],
    runId: string,
  ): HandoffContract {
    return {
      id: `handoff-${Date.now()}`,
      from: fromAgent.agent.id,
      to: toAgent.agent.id,
      objective: toTask.task,
      artefatos: artifacts,
      criterio_de_aceite: toTask.Checklist.join('; '),
      status: 'ready',
      timestamp: new Date().toISOString(),
      runId,
    }
  }

  buildHandoffMarkdown(handoff: HandoffContract): string {
    return `[HANDOFF]
de: ${handoff.from}
para: ${handoff.to}
objetivo: ${handoff.objective}
artefatos: ${handoff.artefatos.join(', ')}
criterio_de_aceite: ${handoff.criterio_de_aceite}
status: ${handoff.status}
[/HANDOFF]`
  }

  parseHandoffFromMarkdown(markdown: string): HandoffContract | null {
    const match = markdown.match(/\[HANDOFF\]([\s\S]*?)\[\/HANDOFF\]/)
    if (!match) return null

    const content = match[1]
    const getField = (field: string): string => {
      const regex = new RegExp(`${field}:\\s*(.+)`)
      const m = content.match(regex)
      return m ? m[1].trim() : ''
    }

    return {
      id: `handoff-parsed-${Date.now()}`,
      from: getField('de'),
      to: getField('para'),
      objective: getField('objetivo'),
      artefatos: getField('artefatos').split(',').map(s => s.trim()),
      criterio_de_aceite: getField('criterio_de_aceite'),
      status: getField('status') as HandoffContract['status'],
      timestamp: new Date().toISOString(),
      runId: '',
    }
  }

  resolveArtifactDependencies(
    fromTask: TaskDefinition,
    toTask: TaskDefinition,
    artifactDir: string,
  ): string[] {
    const fromOutputs = this.parseOutputs(fromTask)
    const toInputs = this.parseInputs(toTask)

    return fromOutputs.filter(output =>
      toInputs.some(input => output.toLowerCase().includes(input.toLowerCase()) || input.toLowerCase().includes(output.toLowerCase())),
    )
  }

  private parseOutputs(task: TaskDefinition): string[] {
    const outputs: string[] = []
    const lines = task.Saida.split('\n')
    for (const line of lines) {
      const match = line.match(/-\s+(\w+):/)
      if (match) outputs.push(match[1])
    }
    return outputs
  }

  private parseInputs(task: TaskDefinition): string[] {
    const inputs: string[] = []
    const lines = task.Entrada.split('\n')
    for (const line of lines) {
      const match = line.match(/-\s+(\w+):/)
      if (match) inputs.push(match[1])
    }
    return inputs
  }
}
