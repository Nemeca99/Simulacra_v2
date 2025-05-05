import json
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, Any, List
import sys


class BenchmarkVisualizer:

    def __init__(self, benchmark_file: Path):
        self.benchmark_file = benchmark_file
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Load benchmark data from JSON file"""
        if not self.benchmark_file.exists():
            print("\n❌ Benchmark file not found!")
            print("\nTo generate benchmark data, run:")
            print("python -m pytest tests\\benchmark_suite.py --benchmark-only --benchmark-json=benchmark.json")
            print("\nEnsure all test dependencies are installed:")
            print("python -m pip install pytest pytest-benchmark plotly kaleido")
            sys.exit(1)

        try:
            with open(self.benchmark_file) as f:
                content = f.read().strip()
                if not content:
                    print("\n❌ Benchmark file is empty!")
                    print("Please run the benchmarks first.")
                    sys.exit(1)

                data = json.loads(content)
                if not isinstance(data, dict) or 'benchmarks' not in data:
                    raise ValueError("Invalid benchmark data format")
                return data

        except json.JSONDecodeError as e:
            print("\n❌ Invalid benchmark data!")
            print(f"Error details: {str(e)}")
            print("\nPlease run the benchmarks again to generate valid data.")
            sys.exit(1)

        except Exception as e:
            print(f"\n❌ Error loading benchmark data: {str(e)}")
            sys.exit(1)

    def create_report(self, output_file: Path) -> None:
        """Generate HTML report with interactive charts"""
        try:
            # Group benchmarks by their group
            groups: Dict[str, List[Dict[str, Any]]] = {}
            for bench in self.data['benchmarks']:
                group = bench.get('group', 'ungrouped')
                if group not in groups:
                    groups[group] = []
                groups[group].append(bench)

            if not groups:
                print("No benchmark data found")
                return

            # Create subplot figure
            fig = make_subplots(
                rows=len(groups),
                cols=1,
                subplot_titles=list(groups.keys()),
                vertical_spacing=0.1
            )

            # Add traces for each group
            for idx, (group_name, benchmarks) in enumerate(groups.items(), 1):
                names = [b['name'].split('::')[-1] for b in benchmarks]
                means = [b['stats']['mean'] * 1000 for b in benchmarks]  # Convert to ms
                stddevs = [b['stats']['stddev'] * 1000 for b in benchmarks]

                # Add bar chart
                fig.add_trace(
                    go.Bar(
                        name=group_name,
                        x=names,
                        y=means,
                        error_y=dict(type='data', array=stddevs),
                        hovertemplate=(
                            "<b>%{x}</b><br>"
                            "Mean: %{y:.2f}ms<br>"
                            "StdDev: %{error_y.array:.2f}ms"
                        )
                    ),
                    row=idx,
                    col=1
                )

            # Update layout
            fig.update_layout(
                title_text="Simulacra Performance Benchmarks",
                showlegend=False,
                height=300 * len(groups),
                template="plotly_dark"
            )

            # Save as HTML
            output_file.parent.mkdir(parents=True, exist_ok=True)
            fig.write_html(
                str(output_file),
                include_plotlyjs=True,
                full_html=True
            )
            print(f"Report generated successfully at: {output_file}")

        except Exception as e:
            print(f"Error creating visualization: {e}")
            sys.exit(1)


def main():
    # Setup paths
    base_dir = Path(__file__).parent.parent
    benchmark_file = base_dir / "benchmark.json"
    output_file = base_dir / "reports" / "benchmark_report.html"

    print("Generating benchmark visualization...")
    print(f"Reading from: {benchmark_file}")
    print(f"Writing to: {output_file}")

    # Create visualization
    visualizer = BenchmarkVisualizer(benchmark_file)
    visualizer.create_report(output_file)


if __name__ == "__main__":
    main()
