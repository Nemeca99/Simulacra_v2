import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def load_benchmark_results(file_path: Path) -> dict:
    """Load benchmark results from JSON file"""
    with open(file_path) as f:
        return json.load(f)

def analyze_results(results: dict, output_dir: Path) -> None:
    """Analyze and display benchmark results"""
    # Group benchmarks by category
    categories = {}
    for bench in results['benchmarks']:
        group = bench.get('group', 'ungrouped')
        if group not in categories:
            categories[group] = []
        categories[group].append({
            'name': bench['name'].split('::')[-1],  # Get just the test name
            'mean': bench['stats']['mean'],
            'stddev': bench['stats']['stddev'],
            'ops': 1.0 / bench['stats']['mean']
        })

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Plot mean times
    x_pos = np.arange(len(categories))
    for i, (cat, benchmarks) in enumerate(categories.items()):
        names = [b['name'] for b in benchmarks]
        means = [b['mean'] * 1000 for b in benchmarks]  # Convert to ms
        ax1.bar(x_pos + i * 0.35, means, width=0.35, label=cat)

    ax1.set_title('Mean Execution Time (ms)')
    ax1.set_yscale('log')
    ax1.legend()

    # Plot operations per second
    for i, (cat, benchmarks) in enumerate(categories.items()):
        names = [b['name'] for b in benchmarks]
        ops = [b['ops'] for b in benchmarks]
        ax2.bar(x_pos + i * 0.35, ops, width=0.35, label=cat)

    ax2.set_title('Operations per Second')
    ax2.set_yscale('log')
    ax2.legend()

    plt.tight_layout()
    plt.savefig(output_dir / 'benchmark_analysis.png')

def main():
    base_dir = Path(__file__).parent.parent
    results_file = base_dir / 'results.json'
    output_dir = base_dir / 'analysis'

    if not results_file.exists():
        print("Running benchmarks first...")
        import subprocess
        subprocess.run([
            'python', '-m', 'pytest',
            'tests/test_performance.py',
            '--benchmark-only',
            f'--benchmark-json={results_file}'
        ])

    results = load_benchmark_results(results_file)
    analyze_results(results, output_dir)
    print(f"Analysis complete. Results saved in {output_dir}")

if __name__ == '__main__':
    main()