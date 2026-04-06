const fs = require('fs');
const path = require('path');

const root = process.cwd();
const squadsRoot = path.join(root, 'squads');

function fail(message) {
  console.error(`[validate-agents] ${message}`);
  process.exit(1);
}

function collectAgentFiles() {
  if (!fs.existsSync(squadsRoot)) {
    fail('Missing ./squads directory');
  }

  const files = [];
  const squads = fs
    .readdirSync(squadsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => entry.name);

  for (const squadName of squads) {
    const agentsDir = path.join(squadsRoot, squadName, 'agents');
    if (!fs.existsSync(agentsDir)) {
      fail(`Missing agents directory in squad '${squadName}'`);
    }

    const agentFiles = fs
      .readdirSync(agentsDir, { withFileTypes: true })
      .filter((entry) => entry.isFile() && entry.name.endsWith('.md'))
      .map((entry) => path.join(agentsDir, entry.name));

    files.push(...agentFiles);
  }

  return files;
}

function validateAgentFile(filePath) {
  const content = fs.readFileSync(filePath, 'utf8');
  const relPath = path.relative(root, filePath);

  if (!content.includes('## Agent Definition')) {
    fail(`Missing '## Agent Definition' in ${relPath}`);
  }

  const yamlMatch = content.match(/```yaml[\s\S]*?```/);
  if (!yamlMatch) {
    fail(`Missing YAML block in ${relPath}`);
  }

  const yamlContent = yamlMatch[0];
  if (!/\bid:\s*[-a-z0-9]+/i.test(yamlContent)) {
    fail(`Missing agent id in YAML block: ${relPath}`);
  }
}

const agentFiles = collectAgentFiles();

if (agentFiles.length === 0) {
  fail('No agent files found');
}

for (const filePath of agentFiles) {
  validateAgentFile(filePath);
}

console.log(`[validate-agents] OK (${agentFiles.length} agent files checked)`);
