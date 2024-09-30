import os
import sys
import ast

# Função para identificar se um método está sendo utilizado em outra parte do código
def is_method_used(method_name, file_contents):
    for line in file_contents:
        if method_name in line and not line.strip().startswith('#'):
            return True
    return False

# Função para analisar arquivos Java em busca de métodos e imports não utilizados
def analyze_java_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        contents = f.readlines()

    imports = set()
    methods = {}
    used_methods = set()

    for line in contents:
        # Captura imports
        if line.startswith("import"):
            imports.add(line.strip())
        # Captura métodos
        if line.strip().startswith("public") or line.strip().startswith("private") or line.strip().startswith("protected"):
            method_name = line.split('(')[0].split()[-1]
            methods[method_name] = methods.get(method_name, 0) + 1

    # Identificando métodos utilizados
    for method in methods.keys():
        if is_method_used(method, contents):
            used_methods.add(method)

    unused_imports = imports
    unused_methods = [method for method in methods if method not in used_methods and not method.endswith("Controller")]

    return unused_imports, unused_methods

# Função para buscar todos os arquivos .java no diretório
def find_java_files(directory):
    java_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.java'):
                java_files.append(os.path.join(root, file))
    return java_files

# Função principal para gerar o relatório
def generate_report(directory, tag):
    java_files = find_java_files(directory)

    unused_imports_files = []
    unused_methods_files = {}

    for file in java_files:
        unused_imports, unused_methods = analyze_java_file(file)

        if unused_imports:
            unused_imports_files.append(file)

        if unused_methods:
            unused_methods_files[file] = unused_methods

    # Criar relatório Markdown
    report_path = "/home/borgarelli/Documents/Suporte/Code Review/relatorio_analisador.md"
    with open(report_path, 'w', encoding='utf-8') as report_file:
        report_file.write(f"# Relatório de Análise de Código\n")
        report_file.write(f"## Projeto: {os.path.basename(directory)}\n")
        report_file.write(f"## Tag: {tag}\n\n")

        if unused_imports_files:
            report_file.write("## Classes que possuem imports não utilizados\n")
            for file in unused_imports_files:
                class_name = os.path.basename(file).replace('.java', '')
                report_file.write(f"  - {class_name}\n")
            report_file.write("\n")

        if unused_methods_files:
            report_file.write("## Classes que possuem métodos não utilizados\n")
            for file, methods in unused_methods_files.items():
                class_name = os.path.basename(file).replace('.java', '')
                report_file.write(f"  - {class_name}\n")
                for method in methods:
                    report_file.write(f"    -- {method}\n")
                report_file.write("\n")  # Adiciona uma quebra de linha extra

    print(f"Relatório gerado em: {report_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python analisador_spring.py <TAG>")
        sys.exit(1)

    tag = sys.argv[1]
    current_directory = os.getcwd()
    generate_report(current_directory, tag)
