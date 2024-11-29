import subprocess


def render_graph(graphviz_path, dot_file, output_file):

    try:
        subprocess.run([graphviz_path, "-Tpng", dot_file, "-o", output_file], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Ошибка при рендеринге графа: {e}")
