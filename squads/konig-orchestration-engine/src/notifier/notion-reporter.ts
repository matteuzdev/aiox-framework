import { readFileSync, existsSync } from 'fs'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

interface NotionActivity {
  squad: string
  task: string
  agent: string
  status: 'completed' | 'failed'
  runId: string
  workflow?: string
  duration?: string
  artifacts: number
  error?: string
  summary?: string
}

export class NotionReporter {
  private token: string
  private activitiesDbId: string | null = null
  private runsDbId: string | null = null

  constructor() {
    this.token = this.loadToken()
    this.loadConfig()
  }

  private loadToken(): string {
    const envPaths = [
      join(__dirname, '../../.env'),
      join(__dirname, '../../../.env'),
      join(process.cwd(), '.env'),
    ]
    for (const p of envPaths) {
      if (existsSync(p)) {
        const content = readFileSync(p, 'utf-8')
        for (const line of content.split('\n')) {
          if (line.startsWith('NOTION_TOKEN=')) {
            return line.split('=')[1].trim()
          }
        }
      }
    }
    return ''
  }

  private loadConfig() {
    const configPaths = [
      join(__dirname, '../../.notion-config.json'),
      join(__dirname, '../../../.notion-config.json'),
      join(process.cwd(), '.notion-config.json'),
    ]
    for (const p of configPaths) {
      if (existsSync(p)) {
        try {
          const config = JSON.parse(readFileSync(p, 'utf-8'))
          this.activitiesDbId = config.crm_activities_db || null
          this.runsDbId = config.runs_database_id || null
        } catch {
          // ignore
        }
      }
    }
  }

  private getHeaders(): Record<string, string> {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Notion-Version': '2022-06-28',
      'Content-Type': 'application/json',
    }
  }

  async reportActivity(activity: NotionActivity): Promise<boolean> {
    if (!this.token || !this.activitiesDbId) {
      console.log('[NOTION] Not configured, skipping report')
      return false
    }

    try {
      const payload = {
        parent: { type: 'database_id', database_id: this.activitiesDbId },
        properties: {
          Atividade: { title: [{ text: { content: `${activity.task}` } }] },
          Tipo: { select: { name: this.mapTaskToType(activity.task) } },
          Status: { select: { name: activity.status === 'completed' ? 'Concluida' : 'Cancelada' } },
          Lead: { rich_text: [{ text: { content: activity.squad } }] },
          Responsavel: { rich_text: [{ text: { content: activity.agent } }] },
          Data: { date: { start: new Date().toISOString().split('T')[0] } },
          Duracao: { rich_text: [{ text: { content: activity.duration || 'N/A' } }] },
          Notas: { rich_text: [{ text: { content: this.buildSummary(activity) } }] },
        },
      }

      const res = await fetch('https://api.notion.com/v1/pages', {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(payload),
      })

      if (res.ok) {
        console.log(`[NOTION] Activity reported: ${activity.task} by ${activity.agent}`)
        return true
      } else {
        const err = await res.text()
        console.log(`[NOTION] Failed to report activity: ${res.status} - ${err.slice(0, 200)}`)
        return false
      }
    } catch (error) {
      console.log(`[NOTION] Error reporting activity: ${error}`)
      return false
    }
  }

  async reportRunComplete(
    squadName: string,
    workflowName: string,
    runId: string,
    tasks: Array<{ task: string; agent: string; status: string; error?: string; outputs?: Record<string, unknown> }>,
    duration: string,
  ): Promise<boolean> {
    if (!this.token || !this.runsDbId) {
      console.log('[NOTION] Runs DB not configured, skipping')
      return false
    }

    try {
      const allCompleted = tasks.every(t => t.status === 'completed')
      const successCount = tasks.filter(t => t.status === 'completed').length
      const errors = tasks.filter(t => t.error).map(t => `${t.task}: ${t.error?.slice(0, 100)}`).join('\n')

      const payload = {
        parent: { type: 'database_id', database_id: this.runsDbId },
        properties: {
          'Run ID': { title: [{ text: { content: runId } }] },
          'Squad': { select: { name: squadName } },
          'Workflow': { rich_text: [{ text: { content: workflowName || 'single-task' } }] },
          'Status': { select: { name: allCompleted ? 'Sucesso' : 'Falhou' } },
          'Inicio': { date: { start: new Date().toISOString().split('T')[0] } },
          'Duracao': { rich_text: [{ text: { content: duration } }] },
          'Tasks Executadas': { number: tasks.length },
          'Tasks com Sucesso': { number: successCount },
          'Erros': { rich_text: [{ text: { content: errors.slice(0, 2000) } }] },
        },
      }

      const res = await fetch('https://api.notion.com/v1/pages', {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(payload),
      })

      if (res.ok) {
        console.log(`[NOTION] Run reported: ${runId} (${squadName})`)
        return true
      } else {
        const err = await res.text()
        console.log(`[NOTION] Failed to report run: ${res.status} - ${err.slice(0, 200)}`)
        return false
      }
    } catch (error) {
      console.log(`[NOTION] Error reporting run: ${error}`)
      return false
    }
  }

  private mapTaskToType(taskName: string): string {
    const lower = taskName.toLowerCase()
    if (lower.includes('design') || lower.includes('criar') || lower.includes('create')) return 'Proposta'
    if (lower.includes('qualif') || lower.includes('analyze') || lower.includes('analise')) return 'Reuniao'
    if (lower.includes('report') || lower.includes('relatorio')) return 'Email'
    if (lower.includes('scrape') || lower.includes('prospect')) return 'Ligacao'
    if (lower.includes('follow') || lower.includes('update')) return 'Follow-up'
    return 'Email'
  }

  private buildSummary(activity: NotionActivity): string {
    const lines = [
      `Squad: ${activity.squad}`,
      `Agente: ${activity.agent}`,
      `Task: ${activity.task}`,
      `Status: ${activity.status}`,
      `Run: ${activity.runId}`,
    ]
    if (activity.workflow) lines.push(`Workflow: ${activity.workflow}`)
    if (activity.duration) lines.push(`Duracao: ${activity.duration}`)
    if (activity.error) lines.push(`Erro: ${activity.error.slice(0, 200)}`)
    if (activity.summary) lines.push(activity.summary)
    return lines.join('\n')
  }
}
