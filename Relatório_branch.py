import os
import re

# Função para percorrer todos os arquivos .java no projeto
def encontrar_arquivos_java(diretorio):
    arquivos_java = []
    for pasta_raiz, _, arquivos in os.walk(diretorio):
        for arquivo in arquivos:
            if arquivo.endswith(".java"):
                arquivos_java.append(os.path.join(pasta_raiz, arquivo))
    return arquivos_java

# Função para ler o conteúdo de um arquivo Java
def ler_arquivo(arquivo):
    with open(arquivo, 'r', encoding='utf-8') as f:
        return f.read()

# Função para encontrar imports não utilizados
def encontrar_imports_nao_utilizados(conteudo):
    imports = re.findall(r'import\s+([\w\.]+);', conteudo)
    classe_corpo = re.sub(r'import\s+[\w\.]+;', '', conteudo)  # Remove a seção de imports para focar no corpo da classe
    imports_nao_utilizados = [imp for imp in imports if imp.split('.')[-1] not in classe_corpo]
    return imports_nao_utilizados

# Função para encontrar métodos declarados no arquivo
def encontrar_metodos_declarados(conteudo):
    metodos = re.findall(r'(public|private|protected)\s+\w+\s+(\w+)\(.*\)', conteudo)
    return [m[1] for m in metodos]

# Função para encontrar métodos utilizados no arquivo
def encontrar_metodos_utilizados(conteudo):
    return re.findall(r'\.(\w+)\(', conteudo)

# Função para obter o nome da classe (nome do arquivo sem o caminho)
def obter_nome_classe(caminho_arquivo):
    return os.path.basename(caminho_arquivo).replace(".java", "")

# Função para analisar cada arquivo Java e verificar imports e métodos não utilizados
def analisar_arquivo_java(arquivo):
    conteudo = ler_arquivo(arquivo)
    nome_classe = obter_nome_classe(arquivo)
    resultado = {
        "arquivo": nome_classe,
        "imports_nao_utilizados": encontrar_imports_nao_utilizados(conteudo),
        "metodos_nao_utilizados": []
    }
    
    # Ignorar controllers e testes para métodos não utilizados
    if "Controller" not in nome_classe and "Test" not in arquivo:
        metodos_declarados = encontrar_metodos_declarados(conteudo)
        metodos_utilizados = encontrar_metodos_utilizados(conteudo)
        
        # Verificar quais métodos declarados não estão sendo utilizados
        metodos_nao_utilizados = [m for m in metodos_declarados if m not in metodos_utilizados]
        resultado["metodos_nao_utilizados"] = metodos_nao_utilizados
    
    return resultado

# Função para gerar o relatório final em formato .txt no novo formato
def gerar_relatorio(resultados, nome_arquivo="relatorio.txt"):
    with open(nome_arquivo, 'w', encoding='utf-8') as relatorio:
        # Seção de imports não utilizados
        relatorio.write("--Classes que possuem imports não utilizados\n")
        for resultado in resultados:
            if resultado["imports_nao_utilizados"]:
                relatorio.write(f"  - {resultado['arquivo']}\n")  # Exibe só o nome da classe
        
        relatorio.write("\n--Classes que possuem métodos não utilizados\n")
        for resultado in resultados:
            if resultado["metodos_nao_utilizados"]:
                relatorio.write(f"  - {resultado['arquivo']}\n")  # Exibe só o nome da classe
                for metodo in resultado["metodos_nao_utilizados"]:
                    relatorio.write(f"    -- {metodo}\n")
                relatorio.write("\n")  # Adiciona uma quebra de linha após os métodos

# Função principal para analisar o projeto
def analisar_projeto(diretorio_projeto):
    arquivos_java = encontrar_arquivos_java(diretorio_projeto)
    resultados = []
    
    for arquivo in arquivos_java:
        resultado = analisar_arquivo_java(arquivo)
        resultados.append(resultado)
    
    gerar_relatorio(resultados)

# Caminho do projeto Spring a ser analisado
diretorio_projeto = "/home/borgarelli/Documents/4Elements/backend/4Elements-configuration"
analisar_projeto(diretorio_projeto)
