import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
import psycopg2.extras

BASE = Path(__file__).resolve().parent
ENV_PATH = BASE.parent / ".env"
load_dotenv(ENV_PATH)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev")

DB = os.getenv("DATABASE_URL")
if not DB:
    raise SystemExit(
        f"Falta DATABASE_URL. Procurei em: {ENV_PATH} | existe={ENV_PATH.exists()}"
    )


def conn():
    return psycopg2.connect(DB)


@app.get("/")
def index():
    with conn() as c:
        with c.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                "SELECT id, nome, preco_unitario FROM produtos WHERE ativo ORDER BY nome"
            )
            produtos = cur.fetchall()
            cur.execute("SELECT id, nome, uf FROM regioes ORDER BY nome")
            regioes = cur.fetchall()
            cur.execute(
                """
                SELECT v.id, v.data_venda, v.quantidade, v.valor_total, v.canal,
                       p.nome AS produto, r.nome AS regiao
                FROM vendas_ficticias v
                JOIN produtos p ON p.id = v.produto_id
                JOIN regioes r ON r.id = v.regiao_id
                ORDER BY v.id DESC
                LIMIT 15
                """
            )
            recentes = cur.fetchall()
            cur.execute(
                """
                SELECT COALESCE(SUM(valor_total),0) AS faturamento,
                       COALESCE(SUM(quantidade),0) AS itens,
                       COUNT(*) AS qtd_vendas
                FROM vendas_ficticias
                """
            )
            kpis = cur.fetchone()
    return render_template(
        "index.html",
        produtos=produtos,
        regioes=regioes,
        recentes=recentes,
        kpis=kpis,
        hoje=date.today().isoformat(),
    )


@app.post("/vendas")
def criar_venda_form():
    try:
        pid = int(request.form["produto_id"])
        rid = int(request.form["regiao_id"])
        data = request.form.get("data_venda") or date.today().isoformat()
        qtd = int(request.form["quantidade"])
        canal = request.form.get("canal") or "loja"
        vend = request.form.get("vendedor") or None
        with conn() as c:
            with c.cursor() as cur:
                cur.execute(
                    "SELECT preco_unitario FROM produtos WHERE id=%s AND ativo",
                    (pid,),
                )
                row = cur.fetchone()
                if not row:
                    flash("Produto inválido.", "danger")
                    return redirect(url_for("index"))
                preco = row[0]
                cur.execute(
                    """
                    INSERT INTO vendas_ficticias
                    (produto_id, regiao_id, data_venda, quantidade, valor_unitario, canal, vendedor)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                    """,
                    (pid, rid, data, qtd, preco, canal, vend),
                )
            c.commit()
        flash("Venda registada!", "success")
    except Exception as e:
        flash(f"Erro: {e}", "danger")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)