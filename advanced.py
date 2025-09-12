from typing import Dict, Callable
from generic_client import MCPTesterClient
from logging import getLogger
import asyncio, time, psutil, os
logger = getLogger(__name__)

async def timeout_tester(client: MCPTesterClient, **kwargs):
    grace = kwargs.get("grace", 5)

    if client.transport_name != "stdio":
        raise RuntimeError("timeout_tester only works with stdio transport")
    
    server_id = kwargs.get("server_id", "1")
    logger.info(f"Running timeout_tester on server {server_id}")

    stdio_params = client.transport_params[server_id]["server_params"] 
    session = client.sessions[server_id]
    stack = client.exit_stacks[server_id]

    proc = find_stdio_child(cmd_stem=stdio_params.command.split(os.sep)[-1].lower())
    base = snapshot(proc)

    # Start a long/expensive call (or supply args that force work)
    task = asyncio.create_task(session.call_tool(tool, args))
    await asyncio.sleep(0.2)  # let it start
    # Cancel (or enforce a timeout)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    # Close the session/transport to simulate disconnect
    await stack.aclose()

    # Poll for decay back toward baseline
    deadline = time.monotonic() + grace
    last = None
    while time.monotonic() < deadline:
        last = snapshot(proc)
        # Heuristic: near-baseline RSS/threads/children and low CPU
        ok_cpu = last.get("cpu", 0) < 2.0
        ok_thr = last.get("thr", 0) <= base.get("thr", 0) + 1
        ok_kids = last.get("kids", 0) <= base.get("kids", 0)
        ok_rss = last.get("rss", 0) <= base.get("rss", 0) * 1.10 + 5_000_000  # +10% / +5MB slack
        if ok_cpu and ok_thr and ok_kids and ok_rss:
            return {"status": "clean", "baseline": base, "final": last}
        await asyncio.sleep(0.2)

    return {"status": "suspect_leak", "baseline": base, "final": last}

## timeout_tester helper functions
def find_stdio_child(cmd_stem: str) -> psutil.Process:
    """
    Find the stdio server process we spawned, to monitor its resource usage.
    Proposed by ChatGPT, adapted by me: likely needs alternation due to my own lack of psutil experience.
    """
    me = psutil.Process(os.getpid())
    time.sleep(0.1)  # tiny pause to let child spawn
    candidates = [c for c in me.children(recursive=False) if c.is_running()]
    # Heuristic: match by exe/cmdline
    for p in candidates:
        try:
            cl = " ".join(p.cmdline()).lower()
            if cmd_stem in cl:
                return p
        except psutil.Error:
            pass
    raise RuntimeError("Could not locate stdio server process")

def snapshot(proc: psutil.Process) -> dict:
    """
    Takes a snapshot of the process resource usage.
    Called before and after timeout cancellation of tool calls to see if resources are freed.
    Proposed by ChatGPT, adapted by me: likely needs alternation due to my own lack of psutil experience.
    """
    try:
        with proc.oneshot():
            rss = proc.memory_info().rss
            cpu = proc.cpu_percent(interval=0.1)  # short sample
            thr = proc.num_threads()
            try:
                fds = proc.num_fds()          # Unix
            except Exception:
                fds = None
            try:
                handles = proc.num_handles()  # Windows
            except Exception:
                handles = None
            children = len(proc.children(recursive=True))
        return {"rss": rss, "cpu": cpu, "thr": thr, "fds": fds, "handles": handles, "kids": children}
    except psutil.Error:
        return {"dead": True}


## cancel_tester --- IGNORE ---
async def cancel_tester(client: MCPTesterClient):
    """
    NOT IMPLEMENTED YET
    Tests the server's ability to handle request cancellations gracefully or mid process
    This would involve sending a request and then cancelling it after a short delay,
    then checking server status and resource usage to ensure it is stable.
    This is to ensure sponge attacking methods don't cause server crashes instability, or failure to free resources.
    """
    raise NotImplementedError("cancel_tester is not implemented yet")

ADVANCED_TOOL_REGISTRY: Dict[str, Callable] = {
    "timeout_tester": timeout_tester,
    "cancel_tester": cancel_tester,
}