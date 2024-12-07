import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import zipfile
import subprocess
from main import (
    extract_nuspec_from_nupkg,
    parse_nuspec_for_dependencies,
    generate_graphviz_code,
    save_graph_to_file
)


class TestDependencyVisualizer(unittest.TestCase):

    def test_extract_nuspec_from_nupkg(self):
        # Создаем фейковый .nupkg архив
        with zipfile.ZipFile('test.nupkg', 'w') as zf:
            zf.writestr('package.nuspec', '<xml>test</xml>')

        # Проверяем успешное извлечение
        result = extract_nuspec_from_nupkg('test.nupkg')
        self.assertEqual(result.decode(), '<xml>test</xml>')

        # Удаляем фейловый архив
        os.remove('test.nupkg')

        # Проверяем случай отсутствия nuspec
        with zipfile.ZipFile('test.nupkg', 'w') as zf:
            zf.writestr('other_file.txt', 'data')

        with self.assertRaises(ValueError):
            extract_nuspec_from_nupkg('test.nupkg')

        os.remove('test.nupkg')

    def test_parse_nuspec_for_dependencies(self):
        # Проверка корректного парсинга XML
        xml_content = """
        <package xmlns="http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd">
            <metadata>
                <dependencies>
                    <group targetFramework="net5.0">
                        <dependency id="TestDep1" version="1.0.0" />
                        <dependency id="TestDep2" version="2.0.0" />
                    </group>
                </dependencies>
            </metadata>
        </package>
        """
        result = parse_nuspec_for_dependencies(xml_content)
        expected = [
            {'target_framework': 'net5.0', 'dependency_id': 'TestDep1', 'version': '1.0.0'},
            {'target_framework': 'net5.0', 'dependency_id': 'TestDep2', 'version': '2.0.0'},
        ]
        self.assertEqual(result, expected)

    def test_generate_graphviz_code(self):
        package_name = "MyPackage"
        dependencies = [
            {'target_framework': 'net5.0', 'dependency_id': 'TestDep1', 'version': '1.0.0'},
            {'target_framework': 'net5.0', 'dependency_id': 'TestDep2', 'version': '2.0.0'},
        ]
        result = generate_graphviz_code(package_name, dependencies)
        expected = (
            "digraph Dependencies {\n"
            '  "MyPackage" [shape=box];\n'
            '  "MyPackage" -> "TestDep1\\nv1.0.0" [label="net5.0"];\n'
            '  "MyPackage" -> "TestDep2\\nv2.0.0" [label="net5.0"];\n'
            "}\n"
        )
        self.assertEqual(result, expected)

    @patch('subprocess.run')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_graph_to_file(self, mock_open_file, mock_subprocess_run):

        mock_subprocess_run.return_value = MagicMock(returncode=0)

        dot_code = "digraph Dependencies { }"
        save_graph_to_file(dot_code, "output.png", "dot")

        # Проверяем, что временный файл был создан
        mock_open_file.assert_called_with("temp_graph.dot", "w")
        mock_open_file().write.assert_called_once_with(dot_code)

        # Проверяем вызов subprocess.run
        mock_subprocess_run.assert_called_once_with(
            ["dot", "-Tpng", "temp_graph.dot", "-o", "output.png"], check=True
        )

    @patch('subprocess.run', side_effect=subprocess.CalledProcessError(1, 'dot'))
    @patch('builtins.print')
    def test_save_graph_to_file_error(self, mock_print, mock_subprocess_run):
        save_graph_to_file("digraph {}", "output.png", "dot")

        # Проверяем что subprocess.run был вызван
        mock_subprocess_run.assert_called_once_with(
            ["dot", "-Tpng", "temp_graph.dot", "-o", "output.png"], check=True
        )

        # Проверяем что сообщение об ошибке было выведено
        mock_print.assert_any_call("Ошибка при генерации графа: Command 'dot' returned non-zero exit status 1.")


if __name__ == "__main__":
    unittest.main()

