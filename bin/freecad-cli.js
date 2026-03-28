#!/usr/bin/env node

/**
 * FreeCAD CLI - JavaScript Wrapper
 *
 * This script wraps the Python FreeCAD CLI for npm/npx usage.
 * It detects Python and runs the freecad_cli Python module.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

// Get the package directory
const packageDir = path.resolve(__dirname, '..');

// Find Python executable
function findPython() {
    const candidates = ['python3', 'python', 'py'];

    for (const python of candidates) {
        try {
            const result = require('child_process').spawnSync(python, ['--version'], {
                encoding: 'utf8'
            });
            if (result.status === 0) {
                return python;
            }
        } catch (e) {
            // Continue to next candidate
        }
    }

    return null;
}

// Main entry point
async function main() {
    const python = findPython();

    if (!python) {
        console.error('Error: Python 3 is not installed or not in PATH.');
        console.error('');
        console.error('To install FreeCAD CLI via npm, you need Python 3 first.');
        console.error('');
        console.error('Installation options:');
        console.error('  1. Install Python: https://www.python.org/downloads/');
        console.error('  2. Use pip to install FreeCAD CLI:');
        console.error('     pip install freecad-cli');
        console.error('  3. Or run directly with Python:');
        console.error('     python -m freecad_cli --help');
        process.exit(1);
    }

    // Build the Python module path
    const freecadCliPath = path.join(packageDir, 'freecad_cli');

    // Pass all command line arguments to Python
    const args = ['-m', 'freecad_cli', ...process.argv.slice(2)];

    // Run Python with the freecad_cli module
    const child = spawn(python, args, {
        cwd: packageDir,
        stdio: 'inherit',
        env: {
            ...process.env,
            PYTHONPATH: packageDir
        }
    });

    child.on('exit', (code) => {
        process.exit(code || 0);
    });

    child.on('error', (err) => {
        console.error('Failed to start Python:', err.message);
        process.exit(1);
    });
}

// Check if this script is run directly
if (require.main === module) {
    main().catch((err) => {
        console.error('Unexpected error:', err);
        process.exit(1);
    });
}

module.exports = { main };
