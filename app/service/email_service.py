import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader
from app.domain.models.usuario.usuario import Usuario  # CORRIGIDO: path correto
from typing import Dict, Any


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_usuario = os.getenv("EMAIL_USUARIO")
        self.email_senha = os.getenv("EMAIL_SENHA")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        self.nome_site = os.getenv("NOME_SITE", "Biblioteca Online")

        # Sistema de templates corrigido
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))

    def enviar_confirmacao_cadastro(self, usuario: Usuario, token: str) -> bool:
        """Envia email de confirmação de cadastro"""
        link_confirmacao = f"{self.base_url}/email/confirmar?token={token}"

        template_data = {
            'nome': usuario.nome,
            'email': usuario.email,
            'link_confirmacao': link_confirmacao,
            'nome_site': self.nome_site,
            'tipo': 'cadastro',
            'tempo_expiracao': '24 horas',
            'cor_botao': '#28a745',  # Verde
            'icone': '✅',
            'titulo': 'Confirme seu email',
            'texto_botao': 'CONFIRMAR EMAIL'
        }

        html_content = self._renderizar_template('emails/confirmacao_base.html', template_data)

        return self._enviar_email(
            destinatario=usuario.email,
            assunto=f"Confirme seu email - {self.nome_site}",
            html_content=html_content
        )

    def enviar_confirmacao_alteracao_email(self, usuario: Usuario, novo_email: str, token: str) -> bool:
        """Envia email de confirmação de alteração"""
        link_confirmacao = f"{self.base_url}/email/confirmar?token={token}"

        template_data = {
            'nome': usuario.nome,
            'email': usuario.email,
            'novo_email': novo_email,
            'link_confirmacao': link_confirmacao,
            'nome_site': self.nome_site,
            'tipo': 'alteracao',
            'tempo_expiracao': '2 horas',
            'cor_botao': '#007bff',  # Azul
            'icone': '🔄',
            'titulo': 'Confirme seu novo email',
            'texto_botao': 'CONFIRMAR ALTERAÇÃO'
        }

        html_content = self._renderizar_template('emails/confirmacao_base.html', template_data)

        return self._enviar_email(
            destinatario=novo_email,
            assunto=f"Confirme alteração de email - {self.nome_site}",
            html_content=html_content
        )

    def enviar_recuperacao_senha(self, usuario: Usuario, token: str) -> bool:
        """Envia email de recuperação de senha"""
        link_recuperacao = f"{self.base_url}/auth/redefinir-senha?token={token}"

        template_data = {
            'nome': usuario.nome,
            'email': usuario.email,
            'link_recuperacao': link_recuperacao,
            'nome_site': self.nome_site,
            'tipo': 'recuperacao_senha',
            'tempo_expiracao': '1 hora',
            'cor_botao': '#dc3545',  # Vermelho
            'icone': '🔐',
            'titulo': 'Redefinir sua senha',
            'texto_botao': 'REDEFINIR SENHA'
        }

        html_content = self._renderizar_template('emails/confirmacao_base.html', template_data)

        return self._enviar_email(
            destinatario=usuario.email,
            assunto=f"Redefinir senha - {self.nome_site}",
            html_content=html_content
        )

    def enviar_notificacao_compra(self, usuario: Usuario, pedido_id: int, valor_total: float) -> bool:
        """Envia notificação de compra realizada"""
        template_data = {
            'nome': usuario.nome,
            'pedido_id': pedido_id,
            'valor_total': valor_total,
            'nome_site': self.nome_site,
            'link_pedido': f"{self.base_url}/pedidos/{pedido_id}",
            'cor_botao': '#28a745',
            'icone': '🛒',
            'titulo': 'Compra realizada com sucesso!',
            'texto_botao': 'VER PEDIDO'
        }

        html_content = self._renderizar_template('emails/notificacao_compra.html', template_data)

        return self._enviar_email(
            destinatario=usuario.email,
            assunto=f"Compra realizada - Pedido #{pedido_id} - {self.nome_site}",
            html_content=html_content
        )

    def _renderizar_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Renderiza template HTML com os dados fornecidos"""
        try:
            template = self.jinja_env.get_template(template_name)
            return template.render(**data)
        except Exception as e:
            print(f"Erro ao renderizar template {template_name}: {e}")
            return self._template_fallback(data)

    def _template_fallback(self, data: Dict[str, Any]) -> str:
        """Template de fallback simples caso não consiga carregar o arquivo"""
        nome = data.get('nome', 'Usuário')
        link = data.get('link_confirmacao') or data.get('link_recuperacao') or data.get('link_pedido', '#')
        nome_site = data.get('nome_site', 'Sistema')
        titulo = data.get('titulo', 'Notificação')

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{titulo}</title>
        </head>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                <h2 style="color: #333; margin-bottom: 20px;">{nome_site}</h2>
                <h3 style="color: #007bff;">{titulo}</h3>
                <p>Olá {nome},</p>
                <p>Clique no botão abaixo para continuar:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{link}" 
                       style="background-color: #007bff; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Continuar
                    </a>
                </div>
                <p style="color: #666; font-size: 12px;">
                    Se você não conseguir clicar no botão, copie e cole este link no navegador:<br>
                    <a href="{link}">{link}</a>
                </p>
                <hr style="margin: 30px 0; border: 1px solid #eee;">
                <p style="color: #666; font-size: 12px;">
                    Este é um email automático, não responda esta mensagem.
                </p>
            </div>
        </body>
        </html>
        """

    def _enviar_email(self, destinatario: str, assunto: str, html_content: str) -> bool:
        """Método privado para enviar email"""
        try:
            if not self.email_usuario or not self.email_senha:
                print("ERRO: Configurações de email não encontradas")
                print("Configure as variáveis: EMAIL_USUARIO e EMAIL_SENHA")
                return False

            msg = MIMEMultipart('alternative')
            msg['From'] = self.email_usuario
            msg['To'] = destinatario
            msg['Subject'] = assunto

            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_usuario, self.email_senha)
                server.send_message(msg)

            print(f"Email enviado com sucesso para: {destinatario}")
            return True

        except smtplib.SMTPAuthenticationError:
            print(f"ERRO: Falha na autenticação SMTP para {destinatario}")
            print("Verifique EMAIL_USUARIO e EMAIL_SENHA")
            return False
        except smtplib.SMTPRecipientsRefused:
            print(f"ERRO: Email destinatário rejeitado: {destinatario}")
            return False
        except Exception as e:
            print(f"Erro ao enviar email para {destinatario}: {e}")
            return False

    def testar_configuracao(self) -> bool:
        """Testa se a configuração de email está funcionando"""
        try:
            if not self.email_usuario or not self.email_senha:
                return False

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_usuario, self.email_senha)

            print("✅ Configuração de email válida")
            return True

        except Exception as e:
            print(f"❌ Erro na configuração de email: {e}")
            return False