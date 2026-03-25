"""
Management command: seed_demo

Cria dois usuários de demonstração com categorias e lançamentos pré-cadastrados,
permitindo que a banca avalie o sistema com dados reais sem precisar cadastrá-los
manualmente.

Uso::

    python manage.py seed_demo

Os usuários criados são:
  - demo1 / demo1@exemplo.com / senha: demo1234
  - demo2 / demo2@exemplo.com / senha: demo1234

O comando é idempotente: se os dados já existirem, nada é duplicado.
"""
import random
from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from Financeiro.lancamentos.models import Categoria, Lancamento
from Usuario.configuracoes.models import PreferenciaUsuario

User = get_user_model()

# ─────────────────────────────────── dados de referência ─────────────────────

USUARIOS = [
    {"username": "demo1", "email": "demo1@exemplo.com", "first_name": "Alice", "last_name": "Demo"},
    {"username": "demo2", "email": "demo2@exemplo.com", "first_name": "Bob",   "last_name": "Demo"},
]

CATEGORIAS = [
    {"nome": "Alimentação",    "cor": "#f97316"},
    {"nome": "Moradia",        "cor": "#6366f1"},
    {"nome": "Transporte",     "cor": "#0ea5e9"},
    {"nome": "Saúde",          "cor": "#22c55e"},
    {"nome": "Lazer",          "cor": "#a855f7"},
    {"nome": "Educação",       "cor": "#eab308"},
    {"nome": "Salário",        "cor": "#14b8a6"},
    {"nome": "Freelance",      "cor": "#ec4899"},
    {"nome": "Investimentos",  "cor": "#64748b"},
    {"nome": "Assinaturas",    "cor": "#ef4444"},
]

LANCAMENTOS_TEMPLATE = [
    # (descricao, tipo, valor_min, valor_max, categoria_nome, defasagem_dias)
    ("Salário mensal",        "receita", 4500, 5500, "Salário",       28),
    ("Freelance projeto web", "receita",  800, 1500, "Freelance",     20),
    ("Dividendos FIIs",       "receita",  150,  400, "Investimentos", 15),
    ("Aluguel",               "despesa", 1200, 1800, "Moradia",       1),
    ("Supermercado",          "despesa",  350,  600, "Alimentação",   3),
    ("Restaurante",           "despesa",   40,  120, "Alimentação",   5),
    ("Combustível",           "despesa",  150,  280, "Transporte",    7),
    ("Uber",                  "despesa",   20,   60, "Transporte",   10),
    ("Plano de saúde",        "despesa",  300,  450, "Saúde",         2),
    ("Academia",              "despesa",   80,  120, "Saúde",        12),
    ("Netflix",               "despesa",   35,   45, "Assinaturas",   4),
    ("Spotify",               "despesa",   20,   25, "Assinaturas",   4),
    ("Curso online",          "despesa",  150,  400, "Educação",     18),
    ("Cinema",                "despesa",   30,   80, "Lazer",        22),
    ("Barzinho",              "despesa",   50,  130, "Lazer",        25),
]


class Command(BaseCommand):
    """Popula o banco com dados de demonstração para dois usuários."""

    help = "Cria usuários e lançamentos de demonstração."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== seed_demo ==="))
        with transaction.atomic():
            for dados in USUARIOS:
                usuario = self._criar_usuario(dados)
                self._criar_preferencia(usuario)
                cats = self._criar_categorias(usuario)
                total = self._criar_lancamentos(usuario, cats)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✔ {usuario.username}: {len(cats)} categorias, {total} lançamentos"
                    )
                )
        self.stdout.write(self.style.SUCCESS("\nSeed concluído! Credenciais: senha = demo1234"))

    # ------------------------------------------------------------------ helpers

    def _criar_usuario(self, dados):
        """Cria o usuário se não existir; retorna o objeto User."""
        usuario, criado = User.objects.get_or_create(
            username=dados["username"],
            defaults={
                "email":      dados["email"],
                "first_name": dados["first_name"],
                "last_name":  dados["last_name"],
            },
        )
        if criado:
            usuario.set_password("demo1234")
            usuario.save()
            self.stdout.write(f"  Usuário criado: {usuario.username}")
        else:
            self.stdout.write(f"  Usuário já existe: {usuario.username}")
        return usuario

    def _criar_preferencia(self, usuario):
        """Cria a preferência de moeda padrão (BRL) para o usuário."""
        PreferenciaUsuario.objects.get_or_create(
            usuario=usuario,
            defaults={"moeda_preferida": "BRL"},
        )

    def _criar_categorias(self, usuario):
        """Cria as categorias padrão para o usuário e devolve dict nome→obj."""
        cats = {}
        for dados in CATEGORIAS:
            cat, _ = Categoria.objects.get_or_create(
                nome=dados["nome"],
                usuario=usuario,
                defaults={"cor": dados["cor"]},
            )
            cats[cat.nome] = cat
        return cats

    def _criar_lancamentos(self, usuario, cats):
        """Cria lançamentos dos últimos 3 meses para o usuário."""
        criados = 0
        hoje = date.today()

        for meses_atras in range(3):
            base = date(hoje.year, hoje.month, 1) - timedelta(days=meses_atras * 30)

            for desc, tipo, vmin, vmax, cat_nome, defasagem in LANCAMENTOS_TEMPLATE:
                data_lanc = base + timedelta(days=defasagem)
                valor = Decimal(str(round(random.uniform(vmin, vmax), 2)))

                categoria = cats.get(cat_nome)
                if not categoria:
                    continue

                existe = Lancamento.objects.filter(
                    descricao=desc,
                    data=data_lanc,
                    usuario=usuario,
                ).exists()

                if not existe:
                    Lancamento.objects.create(
                        descricao=desc,
                        tipo=tipo,
                        valor=valor,
                        data=data_lanc,
                        categoria=categoria,
                        usuario=usuario,
                    )
                    criados += 1

        return criados
