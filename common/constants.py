"""
Constantes de texto do sistema (mensagens e labels visíveis ao usuário).

Centralizar as strings neste módulo facilita manutenção, traduções futuras
e testes.
"""
from django.utils.translation import gettext_lazy as _

# ─── Mensagens de Sucesso ────────────────────────────────────────────────────
MSG_CRIADO_SUCESSO = _("Registro criado com sucesso.")
MSG_ATUALIZADO_SUCESSO = _("Registro atualizado com sucesso.")
MSG_EXCLUIDO_SUCESSO = _("Registro excluído com sucesso.")

# ─── Mensagens de Erro ───────────────────────────────────────────────────────
MSG_ERRO_ACESSO_NEGADO = _("Você não tem permissão para acessar este recurso.")
MSG_ERRO_NAO_ENCONTRADO = _("O registro solicitado não foi encontrado.")
MSG_ERRO_PROCESSAMENTO = _("Ocorreu um erro ao processar a operação. Tente novamente.")
MSG_ERRO_SISTEMA = _("Erro inesperado no sistema. Entre em contato com o suporte.")

# ─── Labels de Interface ─────────────────────────────────────────────────────
LABEL_SALVAR = _("Salvar")
LABEL_CANCELAR = _("Cancelar")
LABEL_EXCLUIR = _("Excluir")
LABEL_EDITAR = _("Editar")
LABEL_NOVO = _("Novo")
LABEL_VOLTAR = _("Voltar")
LABEL_CONFIRMAR = _("Confirmar")
LABEL_EXPORTAR_PDF = _("Exportar PDF")
