import zipfile
import xml.etree.ElementTree as ET
import os
import argparse
import subprocess

def extract_nuspec_from_nupkg(nupkg_path):
    with zipfile.ZipFile(nupkg_path, 'r') as zip_ref:
        # Находим .nuspec файл
        nuspec_file = next((file_name for file_name in zip_ref.namelist() if file_name.endswith('.nuspec')), None)

        if nuspec_file is None:
            raise ValueError("Файл .nuspec не найден в пакете .nupkg")

        # Извлекаем .nuspec файл в память
        with zip_ref.open(nuspec_file) as file:
            return file.read()

def parse_nuspec_for_dependencies(nuspec_content):
    # Загружаем XML с учетом пространства имен
    namespaces = {'ns': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}
    root = ET.fromstring(nuspec_content)

    dependencies = []

    # Ищем все группы зависимостей
    for group in root.findall('.//ns:dependencies/ns:group', namespaces):
        target_framework = group.get('targetFramework', 'Unknown')
        for dep in group.findall('ns:dependency', namespaces):
            dep_id = dep.get('id')
            dep_version = dep.get('version')
            dependencies.append({
                'target_framework': target_framework,
                'dependency_id': dep_id,
                'version': dep_version
            })

    return dependencies

def generate_graphviz_code(package_name, dependencies):
    dot_code = "digraph Dependencies {\n"
    dot_code += f'  "{package_name}" [shape=box];\n'

    for dep in dependencies:
        dep_label = f'{dep["dependency_id"]}\\nv{dep["version"]}'
        dot_code += f'  "{package_name}" -> "{dep_label}" [label="{dep["target_framework"]}"];\n'

    dot_code += "}\n"
    return dot_code

def save_graph_to_file(dot_code, output_file, graph_tool_path):
    dot_file = "temp_graph.dot"

    # Сохраняем Graphviz код во временный файл
    with open(dot_file, "w") as file:
        file.write(dot_code)

    # Вызываем Graphviz для генерации PNG
    try:
        subprocess.run([graph_tool_path, "-Tpng", dot_file, "-o", output_file], check=True)
        print(f"Граф успешно сохранен в {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при генерации графа: {e}")
    finally:
        # Удаляем временный файл
        if os.path.exists(dot_file):
            os.remove(dot_file)

def main():

    parser = argparse.ArgumentParser(
        description="Инструмент для визуализации графа зависимостей пакета .nupkg в формате Graphviz")


    parser.add_argument('graph_tool_path', help="Путь к программе для визуализации графов (например, dot из Graphviz).")
    parser.add_argument('package_name', help="Имя анализируемого пакета (путь к .nupkg файлу).")
    parser.add_argument('output_file', help="Путь к файлу для сохранения изображения графа (формат PNG).")


    args = parser.parse_args()

    nupkg_path = args.package_name
    output_file = args.output_file
    graph_tool_path = args.graph_tool_path

    # Извлекаем.nuspec
    try:
        nuspec_content = extract_nuspec_from_nupkg(nupkg_path)
        dependencies = parse_nuspec_for_dependencies(nuspec_content)

        if dependencies:

            for dep in dependencies:# Генерируем Graphviz код
                dot_code = generate_graphviz_code(os.path.basename(nupkg_path), dependencies)

            # Сохраняем и визуализируем граф
            save_graph_to_file(dot_code, output_file, graph_tool_path)
        else:
            print("Зависимости не найдены.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    main()


# python main.py dot newtonsoft.json.13.0.3.nupkg image.png
