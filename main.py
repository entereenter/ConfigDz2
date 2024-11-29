from dependency_graph import build_dependency_graph
from graph_renderer import render_graph
import argparse
import os


def parse_arguments():
    parser = argparse.ArgumentParser(description="Визуализатор графа зависимостей .NET пакетов")
    parser.add_argument("--graphviz", required=True, help="Путь к программе Graphviz (например, dot)")
    parser.add_argument("--package", required=True, help="Имя анализируемого пакета")
    parser.add_argument("--output", required=True, help="Путь для сохранения изображения графа")
    return parser.parse_args()


def main():
    args = parse_arguments()


    graph_data = build_dependency_graph(args.package)


    dot_file = "dependencies.dot"
    with open(dot_file, "w") as file:
        file.write(graph_data)


    render_graph(args.graphviz, dot_file, args.output)


    os.remove(dot_file)
    print(f"Граф зависимостей сохранен в {args.output}")


if __name__ == "__main__":
    main()
