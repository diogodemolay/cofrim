import json
import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

# ================= CONFIGURAÇÃO =================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_DADOS = os.path.join(BASE_DIR, "cofrim_dados.json")

# ================= DADOS EM MEMÓRIA =================

bancos = []
tipos_movimentacao = []
grupos_contas = []
lancamentos = []

# ================= PERSISTÊNCIA =================

def salvar_dados():
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(
            {
                "bancos": bancos,
                "tipos_movimentacao": tipos_movimentacao,
                "grupos_contas": grupos_contas,
                "lancamentos": lancamentos,
            },
            f,
            ensure_ascii=False,
            indent=2
        )

def carregar_dados():
    global bancos, tipos_movimentacao, grupos_contas, lancamentos

    if not os.path.exists(ARQUIVO_DADOS):
        salvar_dados()
        return

    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
        dados = json.load(f)

    bancos = dados.get("bancos", [])
    tipos_movimentacao = dados.get("tipos_movimentacao", [])
    grupos_contas = dados.get("grupos_contas", [])
    lancamentos = dados.get("lancamentos", [])

# ================= ESTRUTURAS PADRÃO =================

def inicializar_dados_padrao():
    if not bancos:
        bancos.extend([
            {"id": 1, "nome": "Nubank", "apelidos": ["nubank", "nu"]},
            {"id": 2, "nome": "Itaú", "apelidos": ["itau"]},
        ])

    if not tipos_movimentacao:
        tipos_movimentacao.extend([
            {"id": 1, "tipo_principal": "DEBITO", "subtipo": "CARTAO_CREDITO", "palavras_chave": ["cartao", "credito"]},
            {"id": 2, "tipo_principal": "DEBITO", "subtipo": "PIX", "palavras_chave": ["pix"]},
            {"id": 3, "tipo_principal": "CREDITO", "subtipo": "SALARIO", "palavras_chave": ["salario", "recebi", "ganhei"]},
        ])

    if not grupos_contas:
        grupos_contas.extend([
            {
                "grupo": "Alimentação",
                "subgrupos": ["supermercado", "restaurante"],
                "palavras_chave": ["mercado", "supermercado", "restaurante"]
            },
            {
                "grupo": "Lazer",
                "subgrupos": ["cinema", "shows"],
                "palavras_chave": ["cinema", "show"]
            }
        ])

# ================= UTILITÁRIAS =================

import unicodedata

def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

def proximo_id(lista):
    return max([i["id"] for i in lista], default=0) + 1

def identificar_banco(texto):
    texto = normalizar_texto(texto)

    for b in bancos:
        for nome in [b["nome"]] + b["apelidos"]:
            if nome.lower() in texto:
                return b["nome"]

    return None

def identificar_grupo_e_subgrupo(texto):
    texto = normalizar_texto(texto)

    for g in grupos_contas:
        # tenta primeiro subgrupos
        for sg in g["subgrupos"]:
            if normalizar_texto(sg) in texto:
                return g["grupo"], sg

        # depois palavras-chave genéricas
        for p in g.get("palavras_chave", []):
            if normalizar_texto(p) in texto:
                return g["grupo"], p

    return "Outros", "Outros"

# ================= ADMIN — BANCOS =================

def admin_bancos():
    while True:
        print("\n🏦 Bancos")
        print("1 - Listar")
        print("2 - Criar")
        print("3 - Editar")
        print("4 - Apagar")
        print("0 - Voltar")
        op = input("Escolha: ")

        if op == "1":
            for b in bancos:
                print(f'{b["id"]} - {b["nome"]} ({", ".join(b["apelidos"])})')

        elif op == "2":
            nome = input("Nome do banco: ")
            apelidos = input("Apelidos (separados por vírgula): ").split(",")
            bancos.append({
                "id": proximo_id(bancos),
                "nome": nome.strip(),
                "apelidos": [a.strip() for a in apelidos]
            })
            salvar_dados()

        elif op == "3":
            i = int(input("ID do banco a editar: "))
            for b in bancos:
                if b["id"] == i:
                    b["nome"] = input("Novo nome: ")
                    b["apelidos"] = input("Novos apelidos: ").split(",")
                    salvar_dados()

        elif op == "4":
            i = int(input("ID do banco a apagar: "))
            bancos[:] = [b for b in bancos if b["id"] != i]
            salvar_dados()

        elif op == "0":
            return

# ================= ADMIN — TIPOS =================

def admin_tipos():
    while True:
        print("\n🔁 Tipos de Movimentação")
        print("1 - Listar")
        print("2 - Criar")
        print("3 - Editar")
        print("4 - Apagar")
        print("0 - Voltar")
        op = input("Escolha: ")

        if op == "1":
            for t in tipos_movimentacao:
                print(f'{t["id"]} - {t["tipo_principal"]} | {t["subtipo"]}')

        elif op == "2":
            tipo = input("Tipo principal (DEBITO/CREDITO): ").upper()
            subtipo = input("Subtipo: ").upper()
            palavras = input("Palavras-chave: ").split(",")
            tipos_movimentacao.append({
                "id": proximo_id(tipos_movimentacao),
                "tipo_principal": tipo,
                "subtipo": subtipo,
                "palavras_chave": [p.strip() for p in palavras]
            })
            salvar_dados()

        elif op == "3":
            i = int(input("ID a editar: "))
            for t in tipos_movimentacao:
                if t["id"] == i:
                    t["tipo_principal"] = input("Novo tipo principal: ").upper()
                    t["subtipo"] = input("Novo subtipo: ").upper()
                    t["palavras_chave"] = input("Novas palavras: ").split(",")
                    salvar_dados()

        elif op == "4":
            i = int(input("ID a apagar: "))
            tipos_movimentacao[:] = [t for t in tipos_movimentacao if t["id"] != i]
            salvar_dados()

        elif op == "0":
            return

# ================= ADMIN — GRUPOS =================

def admin_grupos():
    while True:
        print("\n🧾 Grupos de Contas")
        print("1 - Listar")
        print("2 - Criar grupo")
        print("3 - Criar subgrupo")
        print("4 - Apagar grupo")
        print("0 - Voltar")
        op = input("Escolha: ")

        if op == "1":
            for g in grupos_contas:
                print(f'{g["grupo"]}: {", ".join(g["subgrupos"])}')

        elif op == "2":
            nome = input("Nome do grupo: ")
            grupos_contas.append({
                "grupo": nome,
                "subgrupos": [],
                "palavras_chave": []
            })
            salvar_dados()

        elif op == "3":
            sub = input("Nome do subgrupo: ")
            for i, g in enumerate(grupos_contas, 1):
                print(f"{i} - {g['grupo']}")
            idx = int(input("Escolha o grupo: ")) - 1
            grupos_contas[idx]["subgrupos"].append(sub)
            grupos_contas[idx]["palavras_chave"].append(sub.lower())
            salvar_dados()

        elif op == "4":
            nome = input("Nome do grupo a apagar: ")
            grupos_contas[:] = [g for g in grupos_contas if g["grupo"] != nome]
            salvar_dados()

        elif op == "0":
            return

# ================= ADMIN — LANÇAMENTOS =================

def admin_lancamentos():
    while True:
        print("\n📋 Lançamentos")
        print("1 - Listar")
        print("2 - Editar")
        print("3 - Apagar")
        print("0 - Voltar")
        op = input("Escolha: ")

        if op == "1":
            print("\nID | Data       | Banco   | Tipo   | Subtipo          | Grupo        | Subgrupo     | Valor")
            print("-" * 90)
            for l in lancamentos:
                print(
                    f"{l['id']:>2} | {l['data'][:10]} | {str(l['banco'] or '-'):7} | "
                    f"{(l['tipo_principal'] or '-'):6} | {(l['subtipo'] or '-'):15} | "
                    f"{l['grupo']:12} | {l['subgrupo']:12} | R$ {l['valor']:.2f}"
                )

        elif op == "2":
            i = int(input("ID do lançamento a editar: "))
            for l in lancamentos:
                if l["id"] == i:
                    print("Campos: data, banco, tipo, subtipo, grupo, subgrupo, valor")
                    campo = input("Qual campo deseja editar? ").lower()

                    if campo == "valor":
                        l["valor"] = float(input("Novo valor: "))
                    elif campo == "data":
                        l["data"] = input("Nova data (YYYY-MM-DD HH:MM): ")
                    elif campo == "banco":
                        l["banco"] = input("Novo banco: ")
                    elif campo == "tipo":
                        l["tipo_principal"] = input("Novo tipo (DEBITO/CREDITO): ").upper()
                    elif campo == "subtipo":
                        l["subtipo"] = input("Novo subtipo: ").upper()
                    elif campo == "grupo":
                        l["grupo"] = input("Novo grupo: ")
                    elif campo == "subgrupo":
                        l["subgrupo"] = input("Novo subgrupo: ")

                    salvar_dados()
                    break

        elif op == "3":
            i = int(input("ID do lançamento a apagar: "))
            lancamentos[:] = [l for l in lancamentos if l["id"] != i]
            salvar_dados()

        elif op == "0":
            return

# ================= MENU PRINCIPAL =================

def menu_admin():
    while True:
        print("\n⚙️ MODO ADMINISTRAÇÃO")
        print("1 - Bancos")
        print("2 - Tipos de Movimentação")
        print("3 - Grupos e Subgrupos")
        print("4 - Lançamentos")
        print("0 - Voltar")
        op = input("Escolha: ")

        if op == "1":
            admin_bancos()
        elif op == "2":
            admin_tipos()
        elif op == "3":
            admin_grupos()
        elif op == "4":
            admin_lancamentos()
        elif op == "0":
            return

def interpretar_data_conversa(texto):
    texto = normalizar_texto(texto)
    hoje = datetime.now()

    if "ontem" in texto:
        return hoje - timedelta(days=1)

    match = re.search(r"(\d{1,2})[\/\-](\d{1,2})", texto)
    if match:
        try:
            return hoje.replace(
                day=int(match.group(1)),
                month=int(match.group(2)),
                hour=10,
                minute=0
            )
        except ValueError:
            pass

    return hoje


def interpretar_periodo_conversa(texto):
    texto = normalizar_texto(texto)
    hoje = datetime.now().date()

    if "hoje" in texto:
        return hoje, hoje

    if "ontem" in texto:
        d = hoje - timedelta(days=1)
        return d, d

    if "essa semana" in texto:
        inicio = hoje - timedelta(days=hoje.weekday())
        return inicio, hoje

    if "semana passada" in texto:
        fim = hoje - timedelta(days=hoje.weekday() + 1)
        inicio = fim - timedelta(days=6)
        return inicio, fim

    if "esse mes" in texto:
        inicio = hoje.replace(day=1)
        return inicio, hoje

    if "mes passado" in texto:
        primeiro_dia_mes = hoje.replace(day=1)
        fim = primeiro_dia_mes - timedelta(days=1)
        inicio = fim.replace(day=1)
        return inicio, fim

    return None, None

def identificar_tipo_e_subtipo(texto):
    texto = normalizar_texto(texto)

    for t in tipos_movimentacao:
        for palavra in t["palavras_chave"]:
            if palavra in texto:
                return t["tipo_principal"], t["subtipo"]

    return None, None

def processar_mensagem(msg):
    texto_norm = normalizar_texto(msg)

    # ================= CONSULTAS =================
    if "quanto" in texto_norm:
        data_inicio, data_fim = interpretar_periodo_conversa(texto_norm)

        grupo_filtro = None
        subgrupo_filtro = None
        subtipo_filtro = None

        # identificar grupo e subgrupo
        for g in grupos_contas:
            grupo_norm = normalizar_texto(g["grupo"])
            if grupo_norm in texto_norm:
                grupo_filtro = g["grupo"]

            for sg in g["subgrupos"]:
                if normalizar_texto(sg) in texto_norm:
                    grupo_filtro = g["grupo"]
                    subgrupo_filtro = sg

        # identificar subtipo
        if "cartao" in texto_norm and "credito" in texto_norm:
            subtipo_filtro = "CARTAO_CREDITO"
        elif "pix" in texto_norm:
            subtipo_filtro = "PIX"

        total = 0.0
        for l in lancamentos:
            data_l = datetime.strptime(l["data"], "%Y-%m-%d %H:%M").date()

            if data_inicio and data_l < data_inicio:
                continue
            if data_fim and data_l > data_fim:
                continue
            if l["tipo_principal"] != "DEBITO":
                continue
            if grupo_filtro and l["grupo"] != grupo_filtro:
                continue
            if subgrupo_filtro and l["subgrupo"] != subgrupo_filtro:
                continue
            if subtipo_filtro and l["subtipo"] != subtipo_filtro:
                continue

            total += l["valor"]

        return f"💸 Você gastou R$ {total:.2f}"

    # ================= LANÇAMENTOS =================
    match = re.search(r"(\d+[.,]?\d*)", texto_norm)
    if not match:
        return "🤔 Não identifiquei um valor."

    valor = float(match.group(1).replace(",", "."))

    tipo, subtipo = identificar_tipo_e_subtipo(texto_norm)
    if not tipo:
        return "🤔 Não entendi se é débito ou crédito."

    banco = identificar_banco(texto_norm)
    grupo, subgrupo = identificar_grupo_e_subgrupo(texto_norm)
    data = interpretar_data_conversa(texto_norm)

    lancamentos.append({
        "id": proximo_id(lancamentos),
        "data": data.strftime("%Y-%m-%d %H:%M"),
        "banco": banco,
        "tipo_principal": tipo,
        "subtipo": subtipo,
        "grupo": grupo,
        "subgrupo": subgrupo,
        "valor": valor,
        "descricao": msg
    })

    salvar_dados()
    return "✔ Lançamento registrado com sucesso."

def modo_conversa():
    print("\n💬 Modo conversa ativo")
    print("Digite lançamentos ou consultas.")
    print("Digite 'sair' para voltar.\n")

    while True:
        msg = input("Você: ").strip()
        if msg.lower() == "sair":
            return

        resposta = processar_mensagem(msg)
        print(f"Cofrim: {resposta}")

# ================= MAIN =================

def main():
    carregar_dados()
    inicializar_dados_padrao()
    salvar_dados()

    while True:
        print("\n=== COFRIM ===")
        print("1 - Modo Conversa")
        print("2 - Modo Administração")
        print("0 - Sair")
        op = input("Escolha: ")

        if op == "1":
            modo_conversa()
        elif op == "2":
            menu_admin()
        elif op == "0":
            break

if __name__ == "__main__":
    main()