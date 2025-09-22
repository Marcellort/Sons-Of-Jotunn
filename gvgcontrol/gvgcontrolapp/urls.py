from django.urls import path


from .views import MemberCreateView, member_success, MemberListView, MemberPaymentUpdateView, MemberListGroupedView, enviar_mensagem_grupo, cancelar_membro
from django.contrib.auth.views import LoginView

app_name = 'membros'

urlpatterns = [
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('membros/cadastrar/', MemberCreateView.as_view(), name='cadastrar'),
    path('membros/sucesso/', member_success, name='sucesso'),
    path('membros/', MemberListView.as_view(), name='listar'),
    path('membros/atualizar_pagamento/', MemberPaymentUpdateView.as_view(), name='atualizar_pagamento'),
    path('membros/agrupados/', MemberListGroupedView.as_view(), name='listar_agrupados'),
    path('membros/enviar_mensagem_grupo/', enviar_mensagem_grupo, name='enviar_mensagem_grupo'),
    path('membros/cancelar/', cancelar_membro, name='cancelar_membro'),
]
