import { rm } from 'fs/promises';
import path from 'path';

const cssPath = path.resolve('web/deploy/css');
const jsPath = path.resolve('web/deploy/js');
const fontsPath = path.resolve('web/deploy/assets/fonts');
const svgPath = path.resolve('web/deploy/assets/svg');
const tempPath = path.resolve('web/temp');

async function clean() {
  console.log('\x1b[31m%s\x1b[0m', 'Cleaning build directory...');
  try {
    await rm(cssPath, { recursive: true, force: true });
    await rm(jsPath, { recursive: true, force: true });
    await rm(fontsPath, { recursive: true, force: true });
    await rm(svgPath, { recursive: true, force: true });
    await rm(tempPath, { recursive: true, force: true });
    console.log('\x1b[32m%s\x1b[0m', '✅ Clean complete.');
  } catch (err) {
    console.error('\x1b[31m%s\x1b[0m', '❌ Error during cleanup:', err);
  }
}

clean();
