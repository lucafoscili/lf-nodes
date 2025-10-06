import os
import shutil

from aiohttp import web
from datetime import datetime
from folder_paths import get_full_path

from server import PromptServer

from ..utils.constants import API_ROUTE_PREFIX, BACKUP_FOLDER
from ..utils.helpers.comfy import get_comfy_dir, get_comfy_list

# region new-backup
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/new-backup")
async def backup_usage_analytics(request):
    try:
        os.makedirs(get_comfy_dir("backup"), exist_ok=True)

        r: dict = await request.post()
        backup_type: str = r.get('backup_type', 'automatic')

        if backup_type == 'automatic':
            for folder_name in os.listdir(get_comfy_dir("backup")):
                if folder_name.startswith('automatic_'):
                    folder_date_str = folder_name.split('_')[1]
                    folder_date = datetime.strptime(folder_date_str, '%Y%m%d')

                    if folder_date.date() == datetime.now().date():
                        return web.json_response({
                            "status": "success",
                            "message": "Automatic backup already created today."
                        }, status=200)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(get_comfy_dir("backup"), f"{backup_type}_{timestamp}")
        os.makedirs(backup_folder, exist_ok=True)

        models_backup_folder = os.path.join(backup_folder, "models")
        analytics_backup_folder = os.path.join(backup_folder, "analytics")
        workflows_backup_folder = os.path.join(backup_folder, "workflows")
        os.makedirs(models_backup_folder, exist_ok=True)
        os.makedirs(analytics_backup_folder, exist_ok=True)
        os.makedirs(workflows_backup_folder, exist_ok=True)

        backed_up_files = []

        directories = [
            ("checkpoints", get_comfy_list("checkpoints")),
            ("embeddings", get_comfy_list("embeddings")),
            ("loras", get_comfy_list("loras"))
        ]

        for folder_name, directory in directories:
            model_subfolder = os.path.join(models_backup_folder, folder_name)
            os.makedirs(model_subfolder, exist_ok=True)

            for model_file in directory:
                model_full_path = get_full_path(folder_name, model_file)

                if model_full_path is None:
                    continue

                file_no_ext = os.path.splitext(model_full_path)[0]
                info_file_path = file_no_ext + ".info"

                if os.path.exists(info_file_path):
                    backup_path = os.path.join(model_subfolder, os.path.basename(info_file_path))

                    shutil.copy2(info_file_path, backup_path)
                    backed_up_files.append(backup_path)

        for root, _, files in os.walk(get_comfy_dir("base")):
            if BACKUP_FOLDER in root:
                continue

            for file_name in files:
                full_path = os.path.join(root, file_name)

                if os.path.exists(full_path) and file_name.endswith(".json"):
                    relative_path = os.path.relpath(full_path, get_comfy_dir("base"))
                    backup_path = os.path.join(analytics_backup_folder, relative_path)
                    backup_dir = os.path.dirname(backup_path)

                    os.makedirs(backup_dir, exist_ok=True)

                    shutil.copy2(full_path, backup_path)
                    backed_up_files.append(backup_path)

        workflows_dir = os.path.join(get_comfy_dir("user"), "default", "workflows")
        if os.path.exists(workflows_dir):
            for root, _, files in os.walk(workflows_dir):
                for file_name in files:
                    workflow_path = os.path.join(root, file_name)
                    if os.path.isfile(workflow_path):
                        relative_path = os.path.relpath(workflow_path, workflows_dir)
                        backup_path = os.path.join(workflows_backup_folder, relative_path)
                        backup_dir = os.path.dirname(backup_path)
                        os.makedirs(backup_dir, exist_ok=True)

                        shutil.copy2(workflow_path, backup_path)
                        backed_up_files.append(backup_path)

        return web.json_response({
            "status": "success",
            "message": f"{backup_type.capitalize()} backup created with {len(backed_up_files)} files.",
            "backup_folder": backup_folder,
            "backed_up_files": backed_up_files
        }, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region get-backup-stats
@PromptServer.instance.routes.get(f"{API_ROUTE_PREFIX}/get-backup-stats")
async def get_backup_stats(request):
    """
    Returns statistics about the backup folder:
    - Total size in bytes
    - Number of backup folders
    - List of backup folders with timestamps
    """
    try:
        backup_dir = get_comfy_dir("backup")

        if not os.path.exists(backup_dir):
            return web.json_response({
                "status": "success",
                "data": {
                    "total_size_bytes": 0,
                    "file_count": 0,
                    "backups": []
                }
            }, status=200)

        total_size = 0
        backups = []

        for folder_name in os.listdir(backup_dir):
            folder_path = os.path.join(backup_dir, folder_name)

            if not os.path.isdir(folder_path):
                continue

            # Calculate folder size
            folder_size = 0
            file_count = 0
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        folder_size += os.path.getsize(file_path)
                        file_count += 1

            total_size += folder_size

            # Parse backup info
            parts = folder_name.split('_')
            backup_type = parts[0] if parts else "unknown"
            timestamp_str = '_'.join(parts[1:]) if len(parts) > 1 else ""

            try:
                # Try to parse timestamp
                if len(timestamp_str) >= 8:
                    date_part = timestamp_str[:8]
                    time_part = timestamp_str[9:15] if len(timestamp_str) > 9 else "000000"
                    timestamp = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                else:
                    timestamp = datetime.now()
            except:
                timestamp = datetime.now()

            backups.append({
                "name": folder_name,
                "type": backup_type,
                "timestamp": timestamp.isoformat(),
                "size_bytes": folder_size,
                "file_count": file_count,
                "path": folder_path
            })

        # Sort backups by timestamp (oldest first)
        backups.sort(key=lambda x: x["timestamp"])

        return web.json_response({
            "status": "success",
            "data": {
                "total_size_bytes": total_size,
                "file_count": len(backups),
                "backups": backups
            }
        }, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion

# region clean-old-backups
@PromptServer.instance.routes.post(f"{API_ROUTE_PREFIX}/clean-old-backups")
async def clean_old_backups(request):
    """
    Removes old backups to maintain a maximum count.
    Keeps the most recent N backups and deletes older ones.
    """
    try:
        r: dict = await request.post()
        max_backups: int = int(r.get('max_backups', 0))

        # If max_backups is 0 or negative, don't delete anything
        if max_backups <= 0:
            return web.json_response({
                "status": "success",
                "message": "Backup retention is disabled (max_backups = 0).",
                "deletedCount": 0,
                "deletedBackups": []
            }, status=200)

        backup_dir = get_comfy_dir("backup")

        if not os.path.exists(backup_dir):
            return web.json_response({
                "status": "success",
                "message": "No backup folder exists.",
                "deletedCount": 0,
                "deletedBackups": []
            }, status=200)

        # Collect all backups with timestamps
        backups = []
        for folder_name in os.listdir(backup_dir):
            folder_path = os.path.join(backup_dir, folder_name)

            if not os.path.isdir(folder_path):
                continue

            # Parse timestamp from folder name
            parts = folder_name.split('_')
            timestamp_str = '_'.join(parts[1:]) if len(parts) > 1 else ""

            try:
                if len(timestamp_str) >= 8:
                    date_part = timestamp_str[:8]
                    time_part = timestamp_str[9:15] if len(timestamp_str) > 9 else "000000"
                    timestamp = datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
                else:
                    # Fallback to folder modification time
                    timestamp = datetime.fromtimestamp(os.path.getmtime(folder_path))
            except:
                # Fallback to folder modification time
                timestamp = datetime.fromtimestamp(os.path.getmtime(folder_path))

            backups.append({
                "name": folder_name,
                "path": folder_path,
                "timestamp": timestamp
            })

        # Sort by timestamp (oldest first)
        backups.sort(key=lambda x: x["timestamp"])

        # Determine how many to delete
        current_count = len(backups)
        to_delete_count = max(0, current_count - max_backups)

        if to_delete_count == 0:
            return web.json_response({
                "status": "success",
                "message": f"No backups need to be deleted. Current count: {current_count}, Maximum: {max_backups}.",
                "deletedCount": 0,
                "deletedBackups": []
            }, status=200)

        # Delete oldest backups
        deleted_backups = []
        for i in range(to_delete_count):
            backup = backups[i]
            try:
                shutil.rmtree(backup["path"])
                deleted_backups.append(backup["name"])
            except Exception as e:
                # Log but continue deleting other backups
                print(f"Failed to delete backup {backup['name']}: {e}")

        return web.json_response({
            "status": "success",
            "message": f"Deleted {len(deleted_backups)} old backup(s). Kept {current_count - len(deleted_backups)} most recent.",
            "deletedCount": len(deleted_backups),
            "deletedBackups": deleted_backups
        }, status=200)

    except Exception as e:
        return web.Response(status=500, text=f"Error: {str(e)}")
# endregion
