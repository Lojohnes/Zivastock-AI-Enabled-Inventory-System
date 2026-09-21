import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.transaction_simulator import TransactionSimulator


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate reproducible ZivaStock transaction data")
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument(
        "--scenario",
        choices=sorted(TransactionSimulator.SUPPORTED_SCENARIOS),
        default="normal",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("../imports/simulated_transactions.csv"))
    args = parser.parse_args()

    dataframe = TransactionSimulator(seed=args.seed).generate(
        days=args.days,
        scenario=args.scenario,
    )
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output, index=False)
    print(f"Generated {len(dataframe)} events")
    print(f"Scenario: {args.scenario}")
    print(f"Seed: {args.seed}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
