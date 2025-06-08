from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .forms import DonateForm

import stripe
import requests

# Configurar a chave secreta da API do Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


def index_view(request):
    return render(request, 'index.html')


def validar_cpf_api(cpf):
    """Valida o CPF usando uma API externa"""
    url = "https://api.exemplo.com/validar_cpf"  # Substituir pela URL real
    try:
        response = requests.post(url, json={"cpf": cpf}, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("valido", False)
    except Exception as e:
        print("Erro ao validar CPF:", e)
        return False


def donate_view(request):
    """Processa o formulário de doação e redireciona para o pagamento"""
    form = DonateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        doacao = form.save()
        request.session['valor_doacao'] = int(doacao.valor * 100)  # em centavos para o Stripe
        request.session['cpf'] = doacao.cpf
        request.session['nome']=doacao.nome.lower()
        return redirect('pagamentos')
    
    return render(request, 'donate.html', {'form': form})


def pagamentos_view(request):
    """Exibe a página de pagamento com informações da doação"""
    valor_centavos = request.session.get('valor_doacao')
    cpf = request.session.get('cpf')
    nome= request.session.get('nome')

    if not valor_centavos or not cpf:
        return redirect('donate')

    context = {
        'valor_centavos': valor_centavos,
        'valor_reais': valor_centavos / 100,  # converter para reais
        'nome':nome,
        'cpf': cpf,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'pagamento.html', context)


def criar_pagamento(request):
    """Cria uma sessão de pagamento com o Stripe"""
    valor_centavos = request.session.get('valor_doacao')

    if not valor_centavos:
        return JsonResponse({'error': 'Valor da doação não encontrado'}, status=400)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {'name': 'Doação'},
                    'unit_amount': valor_centavos,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://semprecrianca-doa-o.onrender.com/pagamentos/',
            cancel_url='https://semprecrianca-doa-o.onrender.com/pagamentos/',
        )
        return JsonResponse({'id': session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def create_checkout_session(request):
    """Exemplo de criação de sessão Stripe com valor fixo"""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'brl',
                'product_data': {'name': 'Produto Teste'},
                'unit_amount': 5000,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='https://semprecrianca-doa-o.onrender.com/pagamentos/',
        cancel_url='https://semprecrianca-doa-o.onrender.com/pagamentos/',
    )
    return JsonResponse({'id': session.id})


@csrf_exempt
def stripe_webhook(request):
    """Recebe notificações do Stripe (webhook)"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = 'sua_chave_de_webhook'  # ou use settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("Pagamento confirmado:", session)

    return HttpResponse(status=200)


def success_view(request):
    return HttpResponse("Obrigado pela sua doação! Seu cadastro foi realizado com sucesso.")
