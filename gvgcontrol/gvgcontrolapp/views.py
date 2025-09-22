from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from .discord_utils import send_discord_message
import threading
import logging
import threading
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.list import ListView
from django.utils.decorators import method_decorator
from django.views import View

from django.views.generic.edit import CreateView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
from .models import Member
from .forms import MemberForm
from django.views.generic import TemplateView

@csrf_exempt
@login_required
def enviar_mensagem_grupo(request):
    if request.method == 'POST':
        group = request.POST.get('group')
        mensagem = request.POST.get('mensagem')
        if not group or not mensagem:
            return HttpResponseBadRequest('Dados incompletos')
        
        now = timezone.now()
        if group == 'ativos_vencidos':
            membros = Member.objects.filter(status='active', expired_in__lt=now)
        elif group == 'ativos_a_vencer':
            membros = Member.objects.filter(status='active', expired_in__gte=now)
        elif group == 'inativos':
            membros = Member.objects.filter(status='inactive')
        else:
            return HttpResponseBadRequest('Grupo inválido')
        enviados = []
        def send_async(discord_id, mensagem):
            try:
                send_discord_message(discord_id, mensagem)
            except Exception as e:
                print(f"Erro ao enviar para {discord_id}: {e}")
        for m in membros:
            t = threading.Thread(target=send_async, args=(m.discord_id, mensagem))
            t.start()
            enviados.append(m.discord_id)
        return JsonResponse({'success': True, 'enviados': enviados})
        return JsonResponse({'success': True, 'enviados': enviados})
    return HttpResponseBadRequest('Método não permitido')

class MemberListGroupedView(LoginRequiredMixin, TemplateView):
    template_name = 'member_list_grouped.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context['ativos_vencidos'] = Member.objects.filter(status='active', expired_in__lt=now).order_by('expired_in')
        context['ativos_a_vencer'] = Member.objects.filter(status='active', expired_in__gte=now).order_by('expired_in')
        context['inativos'] = Member.objects.filter(status='inactive').order_by('nickname')
        return context


@login_required
def member_success(request):
    return render(request, 'member_success.html')

class MemberCreateView(LoginRequiredMixin, CreateView):
    model = Member
    form_class = MemberForm
    template_name = "member_form.html"
    success_url = reverse_lazy("membros:sucesso")

    def form_valid(self, form):
        messages.success(self.request, f"Membro {form.instance.nickname} cadastrado com sucesso!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor, corrija os erros abaixo.")
        return super().form_invalid(form)

class MemberListView(LoginRequiredMixin, ListView):
    model = Member
    template_name = 'member_list.html'
    context_object_name = 'members'


@method_decorator(csrf_exempt, name='dispatch')
class MemberPaymentUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        member_id = request.POST.get('member_id')
        payment_method = request.POST.get('payment_method')
        if not member_id or not payment_method:
            return HttpResponseBadRequest('Dados incompletos')
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return HttpResponseBadRequest('Membro não encontrado')
        member.status = 'active'
        member.paid_at = timezone.now()
        now = timezone.now()
        base_date = member.expired_in if member.expired_in and member.expired_in > now else now
        if payment_method == 'weekly':
            member.expired_in = base_date + timedelta(days=7)
        elif payment_method == 'monthly':
            member.expired_in = base_date + timedelta(days=30)
        member.payment_method = payment_method
        member.save()
        return JsonResponse({'success': True, 'expired_in': member.expired_in.strftime('%d/%m/%Y')})

@csrf_exempt
@login_required
def cancelar_membro(request):
    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        if not member_id:
            return HttpResponseBadRequest('ID não informado')
        try:
            member = Member.objects.get(id=member_id)
        except Member.DoesNotExist:
            return HttpResponseBadRequest('Membro não encontrado')
        member.status = 'inactive'
        member.expired_in = None
        member.save()
        return JsonResponse({'success': True})
    return HttpResponseBadRequest('Método não permitido')