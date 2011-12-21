from google.appengine.ext import db
from google.appengine.api import users

class Cliente(db.Model):
  nome = db.StringProperty(required=True)
  telefone = db.PhoneNumberProperty()
  celular = db.PhoneNumberProperty()
  email = db.EmailProperty(required=True)
  im = db.StringProperty()
  endereco = db.PostalAddressProperty(required=True)
  observacao = db.TextProperty()

class Producao(db.Model):
  arte_pronta = db.BooleanProperty(default=False)
  impresso = db.BooleanProperty(default=False)
  montado = db.BooleanProperty(default=False)
  def pronto(self): return self.arte_pronta and self.impresso and self.montado

class Entrega(db.Model):
  enviado = db.BooleanProperty(default=False)
  recebido = db.BooleanProperty(default=False)
  def entregue(self): return self.enviado and self.recebido

class Pedido(db.Model):
  cliente = db.ReferenceProperty(Cliente, collection_name='pedidos', required=True)
  descricao = db.TextProperty(required=True)
  valor = db.StringProperty(required=True)
  data_entrega = db.DateProperty(required=True)
  data_pedido = db.DateProperty(auto_now_add=True)
  pago = db.BooleanProperty(default=False)
  producao = db.ReferenceProperty(Producao, required=True)
  entrega = db.ReferenceProperty(Entrega, required=True)
  def finalizado(self): return self.producao.pronto() and self.entrega.entregue() and self.pago

def cliente_key(): return db.Key.from_path('Cliente', 'default_cliente')

def pedido_key(): return db.Key.from_path('Pedido', 'default_pedido')
