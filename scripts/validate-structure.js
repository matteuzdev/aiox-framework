const fs = require('fs');
const path = require('path');

const root = process.cwd();
const requiredRootDirs = ['docs', 'squads', '.aiox-core'];
const squadRequiredItems = [
  'squad.yaml',
  'README.md',
  'config',
  'agents',
  'tasks',
  'checklists',
];

function fail(message) {
  console.error(`[validate-structure] ${message}`);
  process.exit(1);
}

function assertExists(targetPath, label) {
  if (!fs.existsSync(targetPath)) {
    fail(`Missing ${label}: ${targetPath}`);
  }
}

for (const dir of requiredRootDirs) {
  assertExists(path.join(root, dir), `root directory '${dir}'`);
}

const squadsRoot = path.join(root, 'squads');
const squads = fs
  .readdirSync(squadsRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name);

if (squads.length === 0) {
  fail('No squads found in ./squads');
}

for (const squadName of squads) {
  const squadPath = path.join(squadsRoot, squadName);
  for (const item of squadRequiredItems) {
    assertExists(path.join(squadPath, item), `squad item '${item}' in ${squadName}`);
  }
}

console.log(`[validate-structure] OK (${squads.length} squads checked)`);
