import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const api = spawn(process.env.PYTHON || 'python', ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], { cwd: root, stdio: 'inherit' });
const vite = spawn(process.execPath, [path.join(root, 'apps/web/node_modules/vite/bin/vite.js'), '--host', '0.0.0.0'], { cwd: path.join(root, 'apps/web'), stdio: 'inherit' });
for (const sig of ['SIGINT', 'SIGTERM'])
    process.on(sig, () => { api.kill(); vite.kill(); process.exit(); });
api.on('error', console.error);
vite.on('error', console.error);
