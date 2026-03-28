#!/usr/bin/env node

/**
 * FreeCAD CLI Benchmark
 *
 * Measures the performance of various CLI operations.
 */

const { spawn, execSync } = require('child_process');
const path = require('path');

const packageDir = path.resolve(__dirname, '..');

// ANSI colors
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function runCommand(cmd, args) {
    const start = process.hrtime.bigint();

    try {
        execSync(`python -m freecad_cli ${args}`, {
            cwd: packageDir,
            encoding: 'utf8',
            timeout: 30000
        });
        const end = process.hrtime.bigint();
        const duration = Number(end - start) / 1e6; // ms
        return { success: true, duration };
    } catch (e) {
        const end = process.hrtime.bigint();
        const duration = Number(end - start) / 1e6;
        return { success: false, duration, error: e.message };
    }
}

async function benchmark() {
    log('\n🧪 FreeCAD CLI Benchmark', 'cyan');
    log('========================\n');

    const iterations = 100;

    // Test cases
    const tests = [
        {
            name: 'Part Creation (Box)',
            args: 'part create --name BenchBox --type Box --params \'{"length": 10, "width": 10, "height": 5}\''
        },
        {
            name: 'Sketch Creation',
            args: 'sketch create --name BenchSketch --plane XY'
        },
        {
            name: 'Draft Line',
            args: 'draft line --name BenchLine --x1 0 --y1 0 --x2 100 --y2 100'
        },
        {
            name: 'Document Info',
            args: 'document info'
        },
        {
            name: 'Object List',
            args: 'object list'
        },
        {
            name: 'JSON Help Output',
            args: '--format json part create --name Test --type Box'
        }
    ];

    const results = [];

    for (const test of tests) {
        log(`\n📊 Testing: ${test.name}`, 'blue');

        const times = [];

        for (let i = 0; i < iterations; i++) {
            const result = runCommand('python', ['-m', 'freecad_cli', ...test.args.split(' ')]);
            times.push(result.duration);

            if (!result.success) {
                log(`  ❌ Failed: ${result.error}`, 'yellow');
                break;
            }
        }

        if (times.length === iterations) {
            // Calculate statistics
            const avg = times.reduce((a, b) => a + b, 0) / times.length;
            const min = Math.min(...times);
            const max = Math.max(...times);

            // Calculate standard deviation
            const variance = times.reduce((sum, t) => sum + Math.pow(t - avg, 2), 0) / times.length;
            const stdDev = Math.sqrt(variance);

            log(`  ✅ Completed ${iterations} iterations`, 'green');
            log(`     Average: ${avg.toFixed(2)} ms`, 'reset');
            log(`     Min: ${min.toFixed(2)} ms`, 'reset');
            log(`     Max: ${max.toFixed(2)} ms`, 'reset');
            log(`     Std Dev: ${stdDev.toFixed(2)} ms`, 'reset');

            results.push({
                name: test.name,
                avg,
                min,
                max,
                stdDev
            });
        }
    }

    // Summary
    log('\n\n📈 Summary', 'cyan');
    log('==========\n');

    // Sort by average time
    results.sort((a, b) => a.avg - b.avg);

    log('Rank | Operation                    | Avg (ms) | Min (ms) | Max (ms) | StdDev');
    log('-----|------------------------------|----------|----------|----------|--------');

    results.forEach((r, i) => {
        log(
            `${String(i + 1).padStart(4)} | ${r.name.padEnd(28)} | ${r.avg.toFixed(2).padStart(8)} | ${r.min.toFixed(2).padStart(8)} | ${r.max.toFixed(2).padStart(8)} | ${r.stdDev.toFixed(2)}`,
            'reset'
        );
    });

    log('\n✅ Benchmark complete!\n');

    // Memory check
    const memUsage = process.memoryUsage();
    log(`Memory Usage:`, 'blue');
    log(`  RSS: ${(memUsage.rss / 1024 / 1024).toFixed(2)} MB`);
    log(`  Heap Used: ${(memUsage.heapUsed / 1024 / 1024).toFixed(2)} MB`);
    log(`  Heap Total: ${(memUsage.heapTotal / 1024 / 1024).toFixed(2)} MB\n`);
}

// Run benchmark
benchmark().catch(console.error);
