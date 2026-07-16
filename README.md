# Sistema web de vendas (PostgreSQL + Flask + Bootstrap + Power BI)

Aplicacao web para registo de vendas com KPIs em tempo real e base pronta para Power BI.

## Stack
- PostgreSQL
- Python + Flask
- Bootstrap 5
- Power BI

## Como rodar (Windows)
1. Criar base PostgreSQL e executar db/01_schema.sql
2. Copiar .env.example para .env e preencher DATABASE_URL
3. pip install -r requirements.txt
4. cd app
5. python app.py
6. Abrir http://127.0.0.1:5000

## Seguranca
Nunca publique o ficheiro .env nem passwords no GitHub.

## Autora
Thamires Santos
