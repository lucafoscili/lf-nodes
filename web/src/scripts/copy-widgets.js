import fs from 'fs-extra';
import path from 'path';

const logColor = '\x1b[34m%s\x1b[0m'; // Cyan

async function copyLfWidgets() {
  try {
    console.log(logColor, '📦 Copying entire @lf-widgets folder...');

    const src = path.resolve('node_modules', '@lf-widgets');
    const dest = path.resolve('web', 'temp', '@lf-widgets');

    await fs.copy(src, dest);
    console.log(logColor, '🚀 Successfully copied entire @lf-widgets folder!');
  } catch (error) {
    console.error(logColor, '❌ Failed to copy LF Widgets:', error);
  }
}

async function copyLfWidgetsSvg() {
  try {
    console.log(logColor, '📦 Copying LF Widgets SVGs...');

    const src = path.resolve('node_modules', '@lf-widgets', 'assets', 'assets', 'svg');
    const dest = path.resolve('web', 'deploy', 'assets', 'svg');

    await fs.copy(src, dest);
    // The package contains four CRLF SVGs. Emit the same LF bytes as Git's
    // release snapshot, regardless of the build host's checkout settings.
    for (const name of await fs.readdir(dest)) {
      if (!name.endsWith('.svg')) continue;
      const target = path.join(dest, name);
      const content = await fs.readFile(target, 'utf8');
      if (content.includes('\r')) {
        await fs.writeFile(target, content.replace(/\r\n?/g, '\n'), 'utf8');
      }
    }
    console.log(logColor, '🚀 Successfully copied LF Widgets SVGs!');
  } catch (error) {
    console.error(logColor, '❌ Failed to copy LF Widgets SVGs:', error);
  }
}

async function copyLfWidgetsFonts() {
  try {
    console.log(logColor, '📦 Copying LF Widgets Fonts...');

    const src = path.resolve('node_modules', '@lf-widgets', 'assets', 'assets', 'fonts');
    const dest = path.resolve('web', 'deploy', 'assets', 'fonts');

    await fs.copy(src, dest);
    console.log(logColor, '🚀 Successfully copied LF Widgets Fonts!');
  } catch (error) {
    console.error(logColor, '❌ Failed to copy LF Widgets Fonts:', error);
  }
}

copyLfWidgets();
copyLfWidgetsFonts();
copyLfWidgetsSvg();
