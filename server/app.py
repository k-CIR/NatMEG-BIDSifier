#!/usr/bin/env python3
"""
Small FastAPI server to run bidsify.py from a remote host and serve a minimal static
frontend. This is the "fast path" for converting the Electron UI into a simple
web-accessible UI.

Endpoints:
 - POST /api/analyze  -> runs bidsify --analyse --config <tempfile>
 - POST /api/run      -> runs bidsify --config <tempfile>
 - POST /api/report   -> runs bidsify --report --config <tempfile>

This file expects the repository root layout: bidsify.py at the project root.
Run with: uvicorn server.app:app --host 0.0.0.0 --port 8080
"""
from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import tempfile
import subprocess
import asyncio
from uuid import uuid4
from typing import Dict, Any
import os
import yaml
from typing import Optional

app = FastAPI(title="NatMEG-BIDSifier Server")

# Serve the included lightweight web UI from / (see web/index.html)
web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
if os.path.isdir(web_dir):
    app.mount('/', StaticFiles(directory=web_dir, html=True), name='web')


class RawConfig(BaseModel):
    config_yaml: str


def _write_temp_config(contents: str) -> str:
    fd, path = tempfile.mkstemp(suffix='.yml', prefix='natmeg_config_')
    with os.fdopen(fd, 'w') as f:
        f.write(contents)
    return path


def _find_bidsify():
    # Try local repository first, then packaged resources
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    candidate = os.path.join(repo_root, 'bidsify.py')
    if os.path.exists(candidate):
        return candidate
    # Fall back to resources path (bundled app)
    # Many packagers place resources near the application binary
    candidate2 = os.path.join(repo_root, 'electron', 'bidsify.py')
    if os.path.exists(candidate2):
        return candidate2
    # Last resort: hope it's on PATH
    return 'bidsify.py'


def _run_bidsify(args, config_path) -> dict:
    bidsify_path = _find_bidsify()
    python = os.environ.get('PYTHON', 'python3')
    cmd = [python, bidsify_path, '--config', config_path] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'cmd': cmd
        }
    except Exception as exc:
        return { 'success': False, 'error': str(exc), 'cmd': cmd }


@app.post('/api/analyze')
async def api_analyze(config: RawConfig):
    path = _write_temp_config(config.config_yaml)
    try:
        out = _run_bidsify(['--analyse'], path)
        return JSONResponse(out)
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


@app.post('/api/run')
async def api_run(config: RawConfig):
    path = _write_temp_config(config.config_yaml)
    try:
        out = _run_bidsify([], path)
        return JSONResponse(out)
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


@app.post('/api/report')
async def api_report(config: RawConfig):
    path = _write_temp_config(config.config_yaml)
    try:
        out = _run_bidsify(['--report'], path)
        return JSONResponse(out)
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


@app.get('/api/ping')
async def ping():
    return { 'ok': True }


# ----------------------------
# Async job queue + websocket log streaming
# ----------------------------

# In-memory job store (for demo / simple server). For production use a persistent
# queue like Redis/Celery/RQ.
JOBS: Dict[str, Dict[str, Any]] = {}


class JobRequest(BaseModel):
    config_yaml: str
    action: Optional[str] = 'run'


async def _stream_subprocess(cmd, job_id: str):
    """Run the command and stream stdout/stderr lines into JOBS[job_id]['logs'] and connected queues."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    async def read_stream(stream, name):
        while True:
            line = await stream.readline()
            if not line:
                break
            text = line.decode(errors='replace')
            JOBS[job_id].setdefault('logs', []).append({'stream': name, 'line': text})
            # forward to all connected client queues
            for q in list(JOBS[job_id].get('clients', [])):
                await q.put(text)

    readers = [read_stream(proc.stdout, 'stdout'), read_stream(proc.stderr, 'stderr')]
    await asyncio.gather(*readers)
    code = await proc.wait()
    JOBS[job_id]['returncode'] = code
    JOBS[job_id]['status'] = 'completed' if code == 0 else 'failed'
    # Notify clients about completion
    done_msg = f"__JOB_DONE__ returncode={code}\n"
    for q in list(JOBS[job_id].get('clients', [])):
        await q.put(done_msg)


@app.post('/api/jobs')
async def create_job(req: JobRequest):
    job_id = str(uuid4())
    JOBS[job_id] = {
        'id': job_id,
        'status': 'queued',
        'logs': [],
        'clients': [],
        'returncode': None,
        'action': req.action,
        'cfg_path': cfg_path,
        'artifacts': []
    }

    # write temporary config
    cfg_path = _write_temp_config(req.config_yaml)

    # determine args
    args = []
    if req.action == 'analyse':
        args = ['--analyse']
    elif req.action == 'report':
        args = ['--report']

    bidsify = _find_bidsify()
    python = os.environ.get('PYTHON', 'python3')
    cmd = [python, bidsify, '--config', cfg_path] + args

    JOBS[job_id]['status'] = 'running'

    async def _background():
        try:
            # parse config to determine expected artifacts
            try:
                with open(cfg_path, 'r') as f:
                    cfg_obj = yaml.safe_load(f)
            except Exception:
                cfg_obj = None

            await _stream_subprocess(cmd, job_id)

            # after completion, try to find canonical artifacts (logs & results)
            if cfg_obj:
                projectRoot = None
                proj = cfg_obj.get('Project') if isinstance(cfg_obj, dict) else None
                if proj and proj.get('Root') and proj.get('Name'):
                    projectRoot = os.path.join(proj.get('Root'), proj.get('Name'))

                logs_dir = os.path.join(projectRoot, 'logs') if projectRoot else None
                conv_name = cfg_obj.get('BIDS', {}).get('Conversion_file') if isinstance(cfg_obj.get('BIDS', {}), dict) else None
                conv_name = conv_name or 'bids_conversion.tsv'
                if logs_dir:
                    cpath = os.path.join(logs_dir, conv_name)
                    results = os.path.join(logs_dir, 'bids_results.json')
                    found = []
                    if os.path.exists(cpath):
                        found.append(cpath)
                    if os.path.exists(results):
                        found.append(results)
                    JOBS[job_id]['artifacts'] = found
        finally:
            try:
                os.unlink(cfg_path)
            except Exception:
                pass

    asyncio.create_task(_background())
    return { 'job_id': job_id }


@app.get('/api/jobs')
async def jobs_list():
    return { 'jobs': [{ 'id': j['id'], 'status': j.get('status'), 'action': j.get('action') } for j in JOBS.values()] }


@app.get('/api/jobs/{job_id}')
async def job_status(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({ 'error': 'not found' }, status_code=404)
    return { 'id': job_id, 'status': job.get('status'), 'returncode': job.get('returncode'), 'logs_count': len(job.get('logs', [])) }


@app.get('/api/jobs/{job_id}/artifacts')
async def job_artifacts(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({ 'error': 'not found' }, status_code=404)
    return { 'artifacts': job.get('artifacts', []) }


@app.get('/api/jobs/{job_id}/artifact')
async def job_artifact_download(job_id: str, index: int = 0):
    job = JOBS.get(job_id)
    if not job:
        return JSONResponse({ 'error': 'not found' }, status_code=404)
    artifacts = job.get('artifacts', [])
    if index < 0 or index >= len(artifacts):
        return JSONResponse({ 'error': 'artifact index out of range' }, status_code=400)
    path = artifacts[index]
    if not os.path.exists(path):
        return JSONResponse({ 'error': 'file not found' }, status_code=404)
    return FileResponse(path, filename=os.path.basename(path))


@app.websocket('/ws/jobs/{job_id}/logs')
async def websocket_logs(ws: WebSocket, job_id: str):
    await ws.accept()
    job = JOBS.get(job_id)
    if not job:
        await ws.send_text('ERROR: job not found')
        await ws.close()
        return

    q = asyncio.Queue()
    job.setdefault('clients', []).append(q)

    try:
        # send backlog first
        for entry in job.get('logs', []):
            await ws.send_text(entry.get('line', ''))

        while True:
            try:
                line = await q.get()
                await ws.send_text(line)
                if isinstance(line, str) and line.startswith('__JOB_DONE__'):
                    break
            except asyncio.CancelledError:
                break
    except WebSocketDisconnect:
        pass
    finally:
        try:
            job['clients'].remove(q)
        except Exception:
            pass

