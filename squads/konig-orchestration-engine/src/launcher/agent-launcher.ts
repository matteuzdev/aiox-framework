import { spawn } from 'child_process'
import { writeFileSync, readFileSync, existsSync } from 'fs'
import { join } from 'path'
import type { AgentLaunchConfig, TaskDefinition } from '../types/index.js'

export class AgentLauncher {
  private mode: 'codex-cli' | 'claude-api'

  constructor(mode: 'codex-cli' | 'claude-api' = 'codex-cli') {
    this.mode = mode
  }

  async launch(config: AgentLaunchConfig): Promise<{ output: string; exitCode: number }> {
    const prompt = this.buildPrompt(config.taskDefinition, config.inputs, config.artifacts)

    if (config.mode === 'claude-api') {
      return this.launchViaApi(config, prompt)
    }
    return this.launchViaCodexCli(config, prompt)
  }

  private buildPrompt(task: TaskDefinition, inputs: Record<string, unknown>, artifacts: Record<string, string>): string {
    let prompt = `You are executing a task for Konig Systems.\n\n`

    prompt += `## Task\n`
    prompt += `${task.task}\n\n`

    if (task.Entrada) {
      prompt += `## Required Inputs\n${task.Entrada}\n\n`
    }

    if (task.Saida) {
      prompt += `## Expected Outputs\n${task.Saida}\n\n`
    }

    if (task.Checklist && task.Checklist.length > 0) {
      prompt += `## Validation Checklist\n${task.Checklist.join('\n')}\n\n`
    }

    if (Object.keys(inputs).length > 0) {
      prompt += `## Provided Inputs\n${JSON.stringify(inputs, null, 2)}\n\n`
    }

    if (Object.keys(artifacts).length > 0) {
      prompt += `## Available Artifacts (from previous tasks)\n`
      for (const [name, path] of Object.entries(artifacts)) {
        prompt += `- ${name}: ${path}\n`
      }
      prompt += '\n'
    }

    prompt += `Execute this task and produce the expected outputs.\n`
    prompt += `Write all output artifacts to the current working directory.\n`

    return prompt
  }

  private async launchViaCodexCli(config: AgentLaunchConfig, prompt: string): Promise<{ output: string; exitCode: number }> {
    const outputFile = join(config.cwd, `.konig-output-${config.runId}.md`)
    const promptFile = join(config.cwd, `.konig-prompt-${config.runId}.txt`)
    writeFileSync(promptFile, prompt)

    const codexCmd = process.platform === 'win32' ? 'codex.cmd' : 'codex'

    return new Promise((resolve) => {
      const args = [
        'exec',
        '--full-auto',
        '--skip-git-repo-check',
        '--output-last-message', outputFile,
        '-',
      ]

      const child = spawn(codexCmd, args, {
        cwd: config.cwd,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env },
        shell: process.platform === 'win32',
      })

      let stderr = ''
      child.stderr?.on('data', (data: Buffer) => {
        stderr += data.toString()
      })

      child.stdin?.write(prompt)
      child.stdin?.end()

      child.on('close', (code: number) => {
        let output = stderr
        if (existsSync(outputFile)) {
          output = readFileSync(outputFile, 'utf-8')
        }
        resolve({ output, exitCode: code || 0 })
      })

      child.on('error', (err: Error) => {
        resolve({ output: `Spawn error: ${err.message}`, exitCode: 1 })
      })
    })
  }

  private async launchViaApi(config: AgentLaunchConfig, prompt: string): Promise<{ output: string; exitCode: number }> {
    const apiKey = process.env.ANTHROPIC_API_KEY
    if (!apiKey) {
      throw new Error('ANTHROPIC_API_KEY not set. Required for claude-api mode.')
    }

    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 8192,
        messages: [{ role: 'user', content: prompt }],
      }),
    })

    if (!response.ok) {
      throw new Error(`Claude API error: ${response.status} ${response.statusText}`)
    }

    const data = await response.json() as { content: Array<{ type: string; text: string }> }
    const output = data.content.map(c => c.text).join('\n')
    return { output, exitCode: 0 }
  }
}
