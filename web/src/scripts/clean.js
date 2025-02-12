import { rm } from 'fs/promises';
import path from 'path';

const deployPath = path.resolve('web/deploy');
const tempPath = path.resolve('web/temp');

async function clean() {
  console.log('\x1b[31m%s\x1b[0m', '🗑 Cleaning build directory...');
  try {
    await rm(deployPath, { recursive: true, force: true });
    await rm(tempPath, { recursive: true, force: true });
    console.log('\x1b[32m%s\x1b[0m', '✅ Clean complete.');
  } catch (err) {
    console.error('\x1b[31m%s\x1b[0m', '❌ Error during cleanup:', err);
  }
}

clean();
