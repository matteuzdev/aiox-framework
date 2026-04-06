import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs'
import { join } from 'path'
import type { TaskDefinition, HandoffContract } from '../types/index.js'

export class ChecklistValidator {
  validate(checklist: string[], artifactDir: string): { passed: boolean; details: string[] } {
    const details: string[] = []
    let allPassed = true

    for (const item of checklist) {
      const cleanItem = item.replace(/^\s*[-*]\s*\[.\]\s*/, '')
      const result = this.evaluateChecklistItem(cleanItem, artifactDir)
      details.push(`${result ? '[x]' : '[ ]'} ${cleanItem}`)
      if (!result) allPassed = false
    }

    return { passed: allPassed, details }
  }

  private evaluateChecklistItem(item: string, artifactDir: string): boolean {
    const lowerItem = item.toLowerCase()

    if (lowerItem.includes('owner') || lowerItem.includes('owner primario')) {
      return this.checkOwnerDefined(artifactDir)
    }

    if (lowerItem.includes('sequencia') || lowerItem.includes('sequence')) {
      return this.checkSequenceDefined(artifactDir)
    }

    if (lowerItem.includes('entrada') || lowerItem.includes('input') || lowerItem.includes('saida') || lowerItem.includes('output')) {
      return this.checkInputsOutputsDefined(artifactDir)
    }

    if (lowerItem.includes('positioning') || lowerItem.includes('cadence') || lowerItem.includes('format')) {
      return this.checkFileContains(artifactDir, ['competitor_map.md', 'viral_patterns.md'])
    }

    if (lowerItem.includes('save') || lowerItem.includes('share') || lowerItem.includes('comment') || lowerItem.includes('driver')) {
      return this.checkFileContains(artifactDir, ['viral_patterns.md'])
    }

    if (lowerItem.includes('evidence') || lowerItem.includes('inference') || lowerItem.includes('separate')) {
      return this.checkFileContains(artifactDir, ['competitor_map.md', 'content_gaps.md'])
    }

    if (lowerItem.includes('gap') || lowerItem.includes('observation')) {
      return this.checkFileContains(artifactDir, ['content_gaps.md'])
    }

    if (lowerItem.includes('assumption') || lowerItem.includes('hidden assumption')) {
      return this.checkFileContains(artifactDir, ['execution_contract.md'])
    }

    if (lowerItem.includes('block') || lowerItem.includes('handoff approval')) {
      return this.checkFileContains(artifactDir, ['execution_contract.md'])
    }

    if (lowerItem.includes('readable') || lowerItem.includes('operator')) {
      return this.checkFileExists(artifactDir, 'execution_contract.md')
    }

    if (lowerItem.includes('parallel') || lowerItem.includes('unnecessary')) {
      return true
    }

    if (lowerItem.includes('risco') || lowerItem.includes('bloqueio') || lowerItem.includes('risk') || lowerItem.includes('blockage')) {
      return this.checkFileContains(artifactDir, ['execution_contract.md', 'blockage_report.md'])
    }

    return true
  }

  private checkFileExists(artifactDir: string, filename: string): boolean {
    return existsSync(join(artifactDir, filename))
  }

  private checkFileContains(artifactDir: string, filenames: string[]): boolean {
    return filenames.some(f => existsSync(join(artifactDir, f)))
  }

  private checkOwnerDefined(artifactDir: string): boolean {
    return this.checkFileContains(artifactDir, ['execution_contract.md', 'route_plan.md', 'owner_map.md'])
  }

  private checkSequenceDefined(artifactDir: string): boolean {
    return this.checkFileContains(artifactDir, ['execution_contract.md', 'route_plan.md', 'sequence.md'])
  }

  private checkInputsOutputsDefined(artifactDir: string): boolean {
    return this.checkFileContains(artifactDir, ['execution_contract.md', 'input_output_map.md'])
  }
}
