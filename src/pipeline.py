import sys
import config
from src.observer import run_checks


def main() -> None:
    data_path = config.PIPELINE["data_path"]

    print("Running Pipeline Health Observer...\n")

    results = run_checks(data_path)

    failed = False
    for result in results:
        icon = {"OK": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(result["status"], "❓")
        print(f"{icon}  [{result['status']}] {result['check']}: {result['details']}")
        if result["status"] == "FAIL":
            failed = True

    print()
    if failed:
        print("One or more checks FAILED. Review the issues above.")
        sys.exit(1)
    else:
        print("All checks passed.")


if __name__ == "__main__":
    main()
