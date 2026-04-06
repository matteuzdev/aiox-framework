const fs = require('fs');
const path = require('path');
const { SquadValidator } = require('../.aiox-core/development/scripts/squad/squad-validator');

async function main() {
  const root = process.cwd();
  const squadsRoot = path.join(root, 'squads');

  if (!fs.existsSync(squadsRoot)) {
    throw new Error('Missing ./squads directory');
  }

  const squadDirs = fs
    .readdirSync(squadsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((entry) => path.join(squadsRoot, entry.name));

  if (squadDirs.length === 0) {
    throw new Error('No squads found in ./squads');
  }

  const validator = new SquadValidator();
  let failed = false;

  for (const squadPath of squadDirs) {
    const result = await validator.validate(squadPath);
    process.stdout.write(`${validator.formatResult(result, squadPath)}\n`);
    if (!result.valid) {
      failed = true;
    }
  }

  if (failed) {
    process.exit(1);
  }

  console.log(`[validate-squads] OK (${squadDirs.length} squads validated)`);
}

main().catch((error) => {
  console.error(`[validate-squads] ${error.message}`);
  process.exit(1);
});
