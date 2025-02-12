import fs from 'fs';
import path from 'path';

const logColor = '\x1b[33m'; // Yellow

const baseDir = path.resolve('web/deploy/js/');

console.log(logColor, '*---------------------------------*');
console.log(logColor, '*      Fixing Import Paths        *');
console.log(logColor, '*---------------------------------*');

// Function to recursively search for JavaScript files
function searchFiles(dir) {
  const results = [];
  const list = fs.readdirSync(dir);

  for (const file of list) {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);

    if (stat.isDirectory()) {
      results.push(...searchFiles(filePath)); // Recursively scan subdirectories
    } else if (file.endsWith('.js')) {
      results.push(filePath); // Add .js files
    }
  }
  return results;
}

// Function to update import/export paths inside files
function updateImports(filePath) {
  let content = fs.readFileSync(filePath, 'utf8');
  const regex = /(import|export)\s+[^'"]*['"]([^'"]+)['"]/g;
  let match;
  let modified = false;

  while ((match = regex.exec(content)) !== null) {
    let importPath = match[2];

    // Ensure relative imports include the `.js` extension
    if (importPath.startsWith('.') && !importPath.endsWith('.js')) {
      importPath += '.js';
      content = content.replace(match[2], importPath);
      modified = true;
    }

    // Fix LF Widgets imports if necessary
    if (importPath.includes('@lf-widgets/') && !importPath.endsWith('.js')) {
      importPath += '/index.js';
      content = content.replace(match[2], importPath);
      modified = true;
    }
  }

  if (modified) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(logColor, `✅ Fixed imports in: ${filePath}`);
  }
}

// Search for all .js files and update their imports
const files = searchFiles(baseDir);
files.forEach(updateImports);

console.log(logColor, '*---*');
console.log(logColor, '🚀 Import paths fixed successfully!');
