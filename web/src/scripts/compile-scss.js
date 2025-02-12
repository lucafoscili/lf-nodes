import { execSync } from 'child_process';
import { existsSync, mkdirSync, readdirSync } from 'fs';
import { join, basename, dirname } from 'path';
import { fileURLToPath } from 'url';

// Establish __dirname equivalent in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const logColor = '\x1b[35m%s\x1b[0m'; // magenta
console.log(logColor, '*---------------------------------*');
console.log(logColor, '*     C o m p i l e   S c s s     *');
console.log(logColor, '*---------------------------------*');

// Directory containing SCSS files
const sassDir = join(__dirname, '../../../node_modules/.bin/sass');
const scssDir = join(__dirname, '../styles');
const cssDir = join(__dirname, '../../deploy/css');

console.log(logColor, '*---*');
console.log(logColor, 'Sass dir: ' + sassDir);
console.log(logColor, 'Scss dir: ' + scssDir);
console.log(logColor, 'Css dir: ' + cssDir);

if (!existsSync(cssDir)) {
  mkdirSync(cssDir, { recursive: true });
}

// Find all SCSS files in the directory
const scssFiles = readdirSync(scssDir)
  .filter((file) => file.endsWith('.scss'))
  .map((file) => join(scssDir, file));

// Compile each SCSS file with output path
scssFiles.forEach((file) => {
  const cssFile = file.replace(/\.scss$/, '.css').replace(scssDir, cssDir);
  console.log(logColor, '*---*');
  console.log(logColor, `Compiling ${file} to ${cssFile}`);
  try {
    execSync(`${sassDir} ${file} ${cssFile}`, { stdio: 'inherit' });
  } catch (error) {
    console.log(logColor, '*---*');
    console.error(logColor, `Error compiling ${file}:`, error);
  }
});

console.log(
  logColor,
  'SCSS Files:',
  scssFiles.map((file) => basename(file)),
);
