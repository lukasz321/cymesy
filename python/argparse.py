import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "This is a simple argparser if you forget what's up."
    )

    # This arg must be present.
    parser.add_argument("ip", type=str, help="Run script on a dpu with given IP.")

    # Expects an argument.
    parser.add_argument("--ip", type=str, help="Run script on a dpu with given IP.")

    # A true/false flag.
    parser.add_argument(
        "--no_api",
        action="store_true",
        help="Do NOT create any records in manufacturing API.",
    )

    args = parser.parse_args()

    parser.print_help()
