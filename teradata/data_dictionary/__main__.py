import sys
import time


def main():
    from .build import build, write_outputs
    from .transforms import build_tables_summary

    t0 = time.time()
    dd = build()
    summary = build_tables_summary(dd)
    print("\nWriting outputs:")
    write_outputs(dd, summary)
    print(f"\nTotal time: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        raise
