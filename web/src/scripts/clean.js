import { rm } from 'fs/promises';
import path from 'path';

const deployRoot = path.resolve('web/deploy');
const tempPath = path.resolve('web/temp');

const targets = [
  path.join(deployRoot, 'css'),
  path.join(deployRoot, 'js'),
  path.join(deployRoot, 'assets/fonts'),
  path.join(deployRoot, 'assets/svg'),
  path.join(deployRoot, 'workflow-runner'),
  tempPath,
];

async function clean() {
  console.log('\x1b[31m%s\x1b[0m', 'Cleaning build directory...');
  try {
    for (const target of targets) {
      await rm(target, { recursive: true, force: true });
    }
    console.log('\x1b[32m%s\x1b[0m', 'Clean complete.');
  } catch (err) {
    console.error('\x1b[31m%s\x1b[0m', 'Error during cleanup:', err);
  }
}

clean();
