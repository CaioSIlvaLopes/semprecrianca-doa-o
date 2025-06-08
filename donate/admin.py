from django.contrib import admin
from donate.models import Doacao

class DoacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'cpf', 'valor')
    search_fields = ('cpf', 'nome')  # "name" → "nome" se o campo do model é "nome"

admin.site.register(Doacao, DoacaoAdmin)
