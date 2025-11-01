import asyncio
import importlib.util
from pathlib import Path
import json


def load_adapter_by_path(path: Path):
    spec = importlib.util.spec_from_file_location("job_store_sqlite", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


async def main():
    # repo root is 5 levels up from this script path
    repo_root = Path(__file__).resolve().parents[5]
    adapter_path = repo_root / "custom_nodes" / "lf-nodes" / "modules" / "workflow_runner" / "services" / "job_store_sqlite.py"
    print("Loading adapter from:", adapter_path)
    mod = load_adapter_by_path(adapter_path)
    # ensure we always close the adapter even if exceptions occur
    try:
        # configure with a local DB file in the repo temp area (adapter will choose default if None)
        try:
            mod.configure(None)
        except Exception as e:
            print("configure() raised:", e)

        run_id = "smoke-test-run"
        print("Creating job", run_id)
        rec = await mod.create_job(run_id, owner_id="smoke-owner")
        print("Created record:", rec)

        print("Setting status -> running")
        seq1 = await mod.set_job_status(run_id, "running")
        print("Running seq ->", seq1)

        print("Setting status -> succeeded")
        seq2 = await mod.set_job_status(run_id, "succeeded", result={"ok": True})
        print("Succeeded seq ->", seq2)

        job = await mod.get_job(run_id)
        print("Final job:")
        try:
            print(json.dumps({
                "run_id": job.run_id,
                "status": job.status,
                "seq": job.seq,
                "owner_id": job.owner_id,
            }, indent=2))
        except Exception:
            print(job)
    finally:
        # close DB connection to avoid leaving locks open
        try:
            await mod.close()
        except Exception as e:
            print("Error closing adapter:", e)


if __name__ == "__main__":
    asyncio.run(main())
