import contextlib
from typing import Dict, List, Tuple

from aiohttp import web

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX

try:  # Optional dependency, required for most endpoints
    import psutil  # type: ignore
except Exception:  # pragma: no cover - psutil should be available, but guard anyway
    psutil = None  # type: ignore

try:  # Optional GPU helpers
    import GPUtil  # type: ignore
except Exception:  # pragma: no cover
    GPUtil = None  # type: ignore

try:
    import pynvml  # type: ignore
except Exception:  # pragma: no cover
    pynvml = None  # type: ignore


def _usage_state_message(resource: str, reason: str) -> web.Response:
    return web.json_response(
        {
            "status": "error",
            "message": f"Unable to collect {resource} statistics: {reason}",
            "data": None,
        },
        status=500,
    )


def _collect_gpu_stats() -> Tuple[List[Dict[str, float]], str]:
    gpus: List[Dict[str, float]] = []
    message = "No GPUs detected."

    if pynvml:
        try:
            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            for index in range(count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(index)
                name = pynvml.nvmlDeviceGetName(handle).decode("utf-8")
                memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                try:
                    utilization = float(pynvml.nvmlDeviceGetUtilizationRates(handle).gpu)
                except Exception:
                    utilization = 0.0

                gpus.append(
                    {
                        "name": name,
                        "index": index,
                        "vram_used": int(memory.used),
                        "vram_total": int(memory.total),
                        "utilization": float(utilization),
                    }
                )

            if gpus:
                message = "GPU statistics retrieved via NVML."
        except Exception as exc:
            message = f"NVML unavailable: {exc}"
        finally:
            with contextlib.suppress(Exception):
                pynvml.nvmlShutdown()

    if not gpus and GPUtil:
        try:
            for gpu in GPUtil.getGPUs():
                total_bytes = int(gpu.memoryTotal * 1024 * 1024)
                used_bytes = int(gpu.memoryUsed * 1024 * 1024)
                gpu_index = int(gpu.id) if getattr(gpu, "id", None) is not None else len(gpus)
                gpus.append(
                    {
                        "name": gpu.name or f"GPU {gpu.id}",
                        "index": gpu_index,
                        "vram_used": used_bytes,
                        "vram_total": total_bytes,
                        "utilization": float(gpu.load * 100.0),
                    }
                )

            if gpus:
                message = "GPU statistics retrieved via GPUtil."
        except Exception as exc:
            message = f"GPU statistics unavailable: {exc}"

    return gpus, message


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/get-gpu-stats")
async def get_gpu_stats(_request):
    try:
        gpus, message = _collect_gpu_stats()
        status = "success"
        if not gpus:
            message = message or "No GPUs detected."
        return web.json_response(
            {
                "status": status,
                "message": message,
                "data": gpus,
            },
            status=200,
        )
    except Exception as exc:
        return _usage_state_message("GPU", str(exc))


def _collect_disk_stats():
    if not psutil:
        raise RuntimeError("psutil is not installed.")

    disks = []
    seen = set()
    for partition in psutil.disk_partitions():
        mountpoint = partition.mountpoint
        if mountpoint in seen:
            continue
        seen.add(mountpoint)

        try:
            usage = psutil.disk_usage(mountpoint)
        except PermissionError:
            continue
        except FileNotFoundError:
            continue

        disks.append(
            {
                "device": partition.device or mountpoint,
                "mountpoint": mountpoint,
                "label": getattr(partition, "fstype", "") or "",
                "used": int(usage.used),
                "total": int(usage.total),
                "percent": float(usage.percent),
            }
        )

    return disks


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/get-disk-stats")
async def get_disk_stats(_request):
    try:
        disks = _collect_disk_stats()
        return web.json_response(
            {
                "status": "success",
                "message": "Disk statistics retrieved successfully.",
                "data": disks,
            },
            status=200,
        )
    except Exception as exc:
        return _usage_state_message("disk", str(exc))


def _collect_cpu_stats():
    if not psutil:
        raise RuntimeError("psutil is not installed.")

    per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    cores = [
        {
            "index": index,
            "usage": float(usage),
        }
        for index, usage in enumerate(per_core)
    ]
    average = float(sum(per_core) / len(per_core)) if per_core else float(psutil.cpu_percent())

    return {
        "cores": cores,
        "average": average,
        "count": psutil.cpu_count(logical=True) or 0,
        "physical_count": psutil.cpu_count(logical=False) or 0,
    }


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/get-cpu-stats")
async def get_cpu_stats(_request):
    try:
        cpu = _collect_cpu_stats()
        return web.json_response(
            {
                "status": "success",
                "message": "CPU statistics retrieved successfully.",
                "data": cpu,
            },
            status=200,
        )
    except Exception as exc:
        return _usage_state_message("CPU", str(exc))


def _collect_ram_stats():
    if not psutil:
        raise RuntimeError("psutil is not installed.")

    memory = psutil.virtual_memory()
    swap = None
    with contextlib.suppress(Exception):
        swap = psutil.swap_memory()

    return {
        "used": int(memory.used),
        "total": int(memory.total),
        "available": int(memory.available),
        "percent": float(memory.percent),
        "swap_used": int(getattr(swap, "used", 0)) if swap else 0,
        "swap_total": int(getattr(swap, "total", 0)) if swap else 0,
    }


@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/get-ram-stats")
async def get_ram_stats(_request):
    try:
        ram = _collect_ram_stats()
        return web.json_response(
            {
                "status": "success",
                "message": "RAM statistics retrieved successfully.",
                "data": ram,
            },
            status=200,
        )
    except Exception as exc:
        return _usage_state_message("RAM", str(exc))

