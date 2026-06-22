from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ROOT_DIR.parent
load_dotenv(PROJECT_DIR / ".env")


def main():
    mongodump = shutil.which("mongodump")
    if not mongodump:
        print("mongodump 未安装，请先安装 MongoDB Database Tools。", file=sys.stderr)
        return 1

    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/?directConnection=true")
    db_name = os.getenv("MONGO_DB_NAME", "school_market")
    backup_root = Path(os.getenv("BACKUP_DIR", ROOT_DIR / "backups")).resolve()
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target_dir = backup_root / f"{db_name}-{timestamp}"
    target_dir.parent.mkdir(parents=True, exist_ok=True)

    command = [
        mongodump,
        "--uri",
        mongo_uri,
        "--db",
        db_name,
        "--out",
        str(target_dir),
        "--gzip",
    ]
    result = subprocess.run(command, check=False)
    if result.returncode != 0:
        print("MongoDB 备份失败，请检查 MONGO_URI、MONGO_DB_NAME 和网络权限。", file=sys.stderr)
        return result.returncode

    print(f"备份完成：{target_dir}")
    print(f"恢复示例：mongorestore --uri \"$MONGO_URI\" --gzip --drop {target_dir / db_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
