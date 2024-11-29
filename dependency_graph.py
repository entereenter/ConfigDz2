def build_dependency_graph(package_name):

    dependencies = {
        "PackageA": ["PackageB", "PackageC"],
        "PackageB": ["PackageD", "PackageE"],
        "PackageC": ["PackageF"],
        "PackageD": [],
        "PackageE": ["PackageF", "PackageG"],
        "PackageF": [],
        "PackageG": []
    }

    graph_lines = ["digraph G {"]
    visited = set()

    def add_dependencies(pkg):
        if pkg in visited:
            return
        visited.add(pkg)
        for dep in dependencies.get(pkg, []):
            graph_lines.append(f'    "{pkg}" -> "{dep}";')
            add_dependencies(dep)

    add_dependencies(package_name)
    graph_lines.append("}")
    return "\n".join(graph_lines)
