
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from data_loader import load_test_cases
from evaluation import run_evaluation
from reporting import print_summary_report


def main():
    """Main orchestrator function."""
    parser = argparse.ArgumentParser(description="Evaluate RAG system using RAGAS")
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose mode')
    args = parser.parse_args()

    try:
        test_cases = load_test_cases()
        print(f"\nLoaded {len(test_cases)} test cases")

        results = run_evaluation(test_cases, verbose=args.verbose)

        print_summary_report(results)

        print("\nEvaluation completed\n")

    except Exception as e:
        print(f"\nError during evaluation: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
