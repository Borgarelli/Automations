import os
import xml.etree.ElementTree as ET
import re
from collections import defaultdict

class SpringBootProjectAnalyzer:
    def __init__(self, project_path, report_path=None):
        self.project_path = project_path
        self.dependencies = []
        self.endpoints = defaultdict(lambda: defaultdict(list))  # Para agrupar RequestMapping e métodos
        self.functionalities = []
        self.internal_dependencies = []  # Para dependências internas
        self.deprecated_items = []  # Para itens deprecated
        self.entities = defaultdict(lambda: defaultdict(list))  # Para armazenar tabelas, colunas e tipos
        self.report_path = report_path or os.path.join(self.project_path, 'relatorio_springboot.txt')

    def analyze_dependencies(self):
        pom_file = os.path.join(self.project_path, 'pom.xml')
        if os.path.exists(pom_file):
            tree = ET.parse(pom_file)
            root = tree.getroot()

            # Ignorar namespaces para facilitar a busca
            namespaces = {'mvn': 'http://maven.apache.org/POM/4.0.0'}
            for dependency in root.findall(".//mvn:dependency", namespaces):
                group_id = dependency.find("mvn:groupId", namespaces).text
                artifact_id = dependency.find("mvn:artifactId", namespaces).text
                version = dependency.find("mvn:version", namespaces).text if dependency.find("mvn:version", namespaces) is not None else "N/A"
                self.dependencies.append(f"{group_id}:{artifact_id}:{version}")

                # Exemplo de identificação de dependências internas (ajuste conforme necessário)
                if 'commons' in artifact_id or 'security' in artifact_id:
                    self.internal_dependencies.append(f"{group_id}:{artifact_id}:{version}")

        else:
            print(f"Arquivo pom.xml não encontrado em {self.project_path}")

    def analyze_functionalities(self):
        for root_dir, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if 'class ' in content:
                                class_name = re.findall(r'class\s+(\w+)', content)
                                if class_name:
                                    if '@RestController' in content or '@Controller' in content:
                                        self.functionalities.append(f"Controller: {class_name[0]}")
                                    elif '@Service' in content:
                                        self.functionalities.append(f"Service: {class_name[0]}")
                                    elif '@Mapper' in content:  # Adiciona suporte para mapeadores
                                        self.functionalities.append(f"Mapper: {class_name[0]}")
                                    
                                    # Verifica se há itens deprecated no código
                                    if '@Deprecated' in content:
                                        self.deprecated_items.append(class_name[0])

                    except Exception as e:
                        print(f"Erro ao ler o arquivo {file_path}: {e}")

    def analyze_endpoints(self):
        for root_dir, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                            # Captura todos os RequestMapping
                            request_mappings = re.findall(r'@RequestMapping\s*\(\s*"([^"]+)"\s*\)', content)

                            # Captura os métodos com mapeamentos específicos
                            method_mappings = re.findall(r'@(GetMapping|PostMapping|PutMapping|DeleteMapping)\s*\(\s*"([^"]+)"\s*\)', content)

                            # Adiciona mapeamento principal
                            for mapping in request_mappings:
                                self.endpoints[mapping]['RequestMapping'].append(f"RequestMapping {mapping}")

                            # Captura todos os métodos HTTP (GetMapping, PostMapping, etc.) e os associa aos respectivos RequestMapping
                            for method_type, route in method_mappings:
                                if method_type:
                                    # Associa o método ao RequestMapping correspondente
                                    for request in request_mappings:
                                        self.endpoints[request][method_type].append(f"{method_type} {route}")
                                        break  # Para evitar adições duplicadas

                    except Exception as e:
                        print(f"Erro ao ler o arquivo {file_path}: {e}")

    def analyze_entities(self):
        for root_dir, dirs, files in os.walk(self.project_path):
            for file in files:
                if file.endswith(".java"):
                    file_path = os.path.join(root_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if '@Entity' in content:
                                table_name = self.extract_table_name(content)
                                columns = self.extract_columns(content)
                                self.entities[table_name]['columns'] = columns

                    except Exception as e:
                        print(f"Erro ao ler o arquivo {file_path}: {e}")

    def extract_table_name(self, content):
        # Captura o nome da tabela da entidade (ajuste conforme necessário)
        table_match = re.search(r'@Table\s*\(\s*name\s*=\s*"([^"]+)"', content)
        if table_match:
            return table_match.group(1)
        return "Desconhecido"

    def extract_columns(self, content):
        # Captura as colunas da tabela da entidade e seus tipos
        columns = []
        column_matches = re.findall(r'@Column\s*\(\s*name\s*=\s*"([^"]+)"\s*\)\s*private\s+(\w+)', content)
        for column_name, column_type in column_matches:
            columns.append((column_name, column_type))

        # Identifica chaves primárias e estrangeiras
        if '@Id' in content:
            primary_key_match = re.search(r'@Id\s*\n\s*@Column\s*\(\s*name\s*=\s*"([^"]+)"', content)
            if primary_key_match:
                columns.append((primary_key_match.group(1), "PRIMARY KEY"))

        foreign_key_matches = re.findall(r'@JoinColumn\s*\(\s*name\s*=\s*"([^"]+)"', content)
        for fk_column in foreign_key_matches:
            columns.append((fk_column, "FOREIGN KEY"))

        return columns

    def generate_report(self):
        try:
            with open(self.report_path, 'w', encoding='utf-8') as report_file:
                report_file.write("Levantamento de funcionalidade 4Elements:\n")
                report_file.write("- Funcionalidades: O que é, o que faz, o que usa, onde usa, de quem é (as2/mwm)\n")

                report_file.write("\n- Dependências externas:\n")
                if self.dependencies:
                    for dependency in self.dependencies:
                        report_file.write(f"  - {dependency}\n")
                else:
                    report_file.write("  Nenhuma dependência externa encontrada.\n")

                report_file.write("\n- Dependências internas:\n")
                if self.internal_dependencies:
                    for dependency in self.internal_dependencies:
                        report_file.write(f"  - {dependency}\n")
                else:
                    report_file.write("  Nenhuma dependência interna encontrada.\n")
                
                report_file.write("\n- RESUMO TÉCNICO: CONTROLLER, SERVICE, MAPPER (TABELAS X, Y)\n")
                report_file.write("\n- DEPRECATED: Identificar que não é mais utilizado\n")
                if self.deprecated_items:
                    for item in self.deprecated_items:
                        report_file.write(f"  - {item}\n")
                else:
                    report_file.write("  Nenhum item deprecated encontrado.\n")

                report_file.write("\n- Entradas: API - ENDPOINTS - JOB/SCHEDULERS - MENSAGERIA - PULLING - TCP/IP\n")

                report_file.write("\n### Endpoints:\n")
                if self.endpoints:
                    for request_mapping, methods in self.endpoints.items():
                        report_file.write(f"- RequestMapping {request_mapping}\n")
                        
                        report_file.write(f"  - Gets\n")
                        if 'GetMapping' in methods:
                            for get_route in methods['GetMapping']:
                                report_file.write(f"    {get_route}\n")
                        report_file.write("\n")  # Quebra de linha após Gets

                        report_file.write(f"  - Posts\n")
                        if 'PostMapping' in methods:
                            for post_route in methods['PostMapping']:
                                report_file.write(f"    {post_route}\n")
                        report_file.write("\n")  # Quebra de linha após Posts

                        report_file.write(f"  - Deletes\n")
                        if 'DeleteMapping' in methods:
                            for delete_route in methods['DeleteMapping']:
                                report_file.write(f"    {delete_route}\n")
                        report_file.write("\n")  # Quebra de linha após Deletes

                        report_file.write(f"  - Puts\n")
                        if 'PutMapping' in methods:
                            for put_route in methods['PutMapping']:
                                report_file.write(f"    {put_route}\n")
                        report_file.write("\n")  # Quebra de linha após Puts

                else:
                    report_file.write("  Nenhum endpoint encontrado.\n")

                report_file.write("\n### Tabelas e Colunas:\n")
                if self.entities:
                    for table, details in self.entities.items():
                        report_file.write(f"Tabela: {table}\n")
                        if 'columns' in details:
                            for column, column_type in details['columns']:
                                report_file.write(f"  Coluna: {column} ({column_type})\n")
                        report_file.write("\n")  # Quebra de linha após cada tabela
                else:
                    report_file.write("  Nenhuma tabela encontrada.\n")

                report_file.write("\nRelatório gerado com sucesso em: {self.report_path}\n")

        except Exception as e:
            print(f"Erro ao gerar o relatório: {e}")

    def run(self):
        self.analyze_dependencies()
        self.analyze_functionalities()
        self.analyze_endpoints()
        self.analyze_entities()  # Analisando entidades para tabelas e colunas
        self.generate_report()

if __name__ == "__main__":
    # Substitua pelo caminho do seu projeto Spring Boot
    project_path = '/home/borgarelli/Documents/4Elements/backend/4Elements-configuration'
    
    analyzer = SpringBootProjectAnalyzer(project_path)
    analyzer.run()