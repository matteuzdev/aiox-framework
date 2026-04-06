import { Command } from 'commander'
import chalk from 'chalk'
import { SquadParser } from '../parser/squad-parser.js'
import { TaskRunner } from '../orchestrator/task-runner.js'
import { RunStore } from '../state/run-store.js'
import { HandoffManager } from '../router/handoff-manager.js'
import { join, dirname } from 'path'
import { fileURLToPath } from 'url'
import { existsSync } from 'fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

export function createCLI(): Command {
  const program = new Command()

  const squadsRoot = process.env.KONIG_SQUADS_ROOT || join(__dirname, '..', '..', '..', '..', 'squads')
  const runsDir = process.env.KONIG_RUNS_ROOT || join(__dirname, '..', '..', '..', '..', 'runs')
  
  if (!existsSync(squadsRoot)) {
    console.error(chalk.red(`Error: squads directory not found at ${squadsRoot}`))
    console.error(chalk.yellow(`Please run from the squads directory or set KONIG_SQUADS_ROOT`))
    process.exit(1)
  }

  program
    .name('konig')
    .description('Konig Systems - Execution Engine')
    .version('0.1.0')

  program
    .command('list')
    .description('List squads, tasks, or agents')
    .argument('<type>', 'What to list: squads, tasks, agents')
    .option('--squad <name>', 'Filter by squad name')
    .action((type, opts) => {
      const parser = new SquadParser(squadsRoot)

      if (type === 'squads') {
        const squads = parser.listAllSquads()
        console.log(chalk.bold('\nKonig Systems - Squads\n'))
        for (const squad of squads) {
          const manifest = parser.parseSquadManifest(squad)
          console.log(chalk.cyan(`  ${manifest.name}`))
          console.log(chalk.gray(`    ${manifest.description || 'No description'}`))
          const agentCount = manifest.components?.agents?.length || 0
          const taskCount = manifest.components?.tasks?.length || 0
          console.log(chalk.gray(`    ${agentCount} agents, ${taskCount} tasks`))
          console.log('')
        }
      } else if (type === 'tasks') {
        if (!opts.squad) {
          console.error(chalk.red('Error: --squad is required for listing tasks'))
          process.exit(1)
        }
        const squad = parser.parseSquadFull(opts.squad)
        console.log(chalk.bold(`\n${opts.squad} - Tasks\n`))
        for (const task of squad.tasks) {
          console.log(chalk.cyan(`  *${task.command}`))
          console.log(chalk.gray(`    ${task.task}`))
          console.log(chalk.gray(`    Agent: ${task.responsavel}`))
          console.log('')
        }
      } else if (type === 'agents') {
        if (!opts.squad) {
          console.error(chalk.red('Error: --squad is required for listing agents'))
          process.exit(1)
        }
        const squad = parser.parseSquadFull(opts.squad)
        console.log(chalk.bold(`\n${opts.squad} - Agents\n`))
        for (const agent of squad.agents) {
          console.log(chalk.cyan(`  @${agent.agent.id}`))
          console.log(chalk.gray(`    ${agent.agent.title}`))
          console.log(chalk.gray(`    ${agent.persona.role}`))
          console.log('')
        }
      }
    })

  program
    .command('run')
    .description('Run a task or workflow')
    .argument('<type>', 'What to run: task, workflow')
    .argument('<target>', 'Task file or workflow name')
    .option('--squad <name>', 'Squad name (required)')
    .option('--input <json>', 'Input parameters as JSON')
    .option('--niche <value>', 'Niche parameter')
    .option('--objective <value>', 'Objective parameter')
    .action(async (type, target, opts) => {
      if (!opts.squad) {
        console.error(chalk.red('Error: --squad is required'))
        process.exit(1)
      }

      const runner = new TaskRunner(squadsRoot, runsDir)
      let inputs: Record<string, unknown> = {}
      if (opts.input) {
        try {
          inputs = JSON.parse(opts.input)
        } catch {
          console.error(chalk.red('Error: invalid JSON for --input'))
          process.exit(1)
        }
      }
      if (opts.niche) inputs.niche = opts.niche
      if (opts.objective) inputs.objective = opts.objective

      if (type === 'task') {
        console.log(chalk.bold('\nKonig Systems - Running Task\n'))
        await runner.runTask(opts.squad, target, inputs, {}, opts.mode)
      } else if (type === 'workflow') {
        console.log(chalk.bold('\nKonig Systems - Running Workflow\n'))
        await runner.runWorkflow(opts.squad, target, inputs, opts.mode)
      }
    })

  program
    .command('status')
    .description('Show run status')
    .option('--squad <name>', 'Filter by squad')
    .option('--run <id>', 'Show specific run')
    .action((opts) => {
      const store = new RunStore(runsDir)

      if (opts.squad && opts.run) {
        const run = store.loadRun(opts.squad, opts.run)
        if (!run) {
          console.log(chalk.yellow(`Run not found: ${opts.run}`))
          return
        }
        console.log(chalk.bold(`\nRun: ${run.id}\n`))
        console.log(chalk.cyan(`  Squad: ${run.squad}`))
        console.log(chalk.cyan(`  Status: ${run.status}`))
        console.log(chalk.cyan(`  Started: ${run.startedAt}`))
        console.log('')
        for (const task of run.tasks) {
          const statusColor = task.status === 'completed' ? chalk.green : task.status === 'failed' ? chalk.red : chalk.yellow
          console.log(`  ${statusColor(task.status)} ${task.task} (${task.agent})`)
        }
      } else if (opts.squad) {
        const runs = store.listRuns(opts.squad)
        console.log(chalk.bold(`\n${opts.squad} - Runs\n`))
        for (const run of runs) {
          console.log(chalk.cyan(`  ${run.id}`))
          console.log(chalk.gray(`    Status: ${run.status} | Tasks: ${run.tasks.length}`))
          console.log('')
        }
      } else {
        console.log(chalk.yellow('Use --squad to filter runs'))
      }
    })

  program
    .command('route')
    .description('Route work through squads (orchestration)')
    .argument('<objective>', 'What needs to be achieved')
    .option('--urgency <level>', 'Timing urgency: low, medium, high', 'medium')
    .option('--assets <json>', 'Current assets as JSON')
    .action(async (objective, opts) => {
      const parser = new SquadParser(squadsRoot)
      const squads = parser.listAllSquads()

      console.log(chalk.bold('\nKonig Systems - Work Routing\n'))
      console.log(chalk.cyan(`  Objective: ${objective}`))
      console.log(chalk.cyan(`  Urgency: ${opts.urgency}`))
      console.log('')

      const manifest = parser.parseSquadManifest('konig-orchestration-core')
      console.log(chalk.bold('  Recommended route:\n'))
      console.log(chalk.gray(`    1. konig-orchestration-core (route work)`))
      console.log(chalk.gray(`    2. konig-context-core (gather context)`))
      console.log(chalk.gray(`    3. konig-planning-core (create plan)`))
      console.log(chalk.gray(`    4. [target squad based on objective]`))
      console.log(chalk.gray(`    5. konig-delivery-factory-core (validate done)`))
      console.log('')

      console.log(chalk.bold('  Available squads:\n'))
      for (const squad of squads) {
        const m = parser.parseSquadManifest(squad)
        console.log(chalk.cyan(`    ${m.name}`))
        console.log(chalk.gray(`      ${m.description}`))
        console.log('')
      }
    })

  return program
}
