/**
 * Post-install script for freecad-cli
 *
 * This script runs after npm install and can:
 * - Check Python installation
 * - Install Python dependencies
 * - Set up the CLI tool
 */

const { execSync } = require('child_process');
const path = require('path');

const packageDir = path.resolve(__dirname, '..');

console.log('🔧 FreeCAD CLI Installation');
console.log('=========================\n');

// Check Python
console.log('📦 Checking Python installation...');
try {
    const pythonVersion = execSync('python3 --version 2>&1 || python --version 2>&1', {
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe']
    }).trim();
    console.log(`✅ Python found: ${pythonVersion}`);
} catch (e) {
    console.log('⚠️  Python not found. Please install Python 3.8+ to use freecad-cli.');
    console.log('   Download: https://www.python.org/downloads/\n');
}

// Install Python dependencies
console.log('\n📚 Installing Python dependencies...');
try {
    execSync('pip install click 2>&1', {
        cwd: packageDir,
        stdio: 'inherit'
    });
    console.log('✅ Dependencies installed\n');
} catch (e) {
    console.log('⚠️  Could not install Python dependencies automatically.');
    console.log('   Please run manually: pip install click\n');
}

console.log('✨ Installation complete!');
console.log('\nUsage:');
console.log('  npx freecad-cli --help');
console.log('  npm exec -- freecad-cli -- --help');
console.log('\nFor more options, see: https://github.com/MiniMax-AI/freecad-cli');
