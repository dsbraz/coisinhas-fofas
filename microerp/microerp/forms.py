from wtforms import Form, TextField, BooleanField, DateField, FormField, validators
from wtforms.ext.appengine import db, fields
from models import Cliente, Producao, Entrega
from datetime import datetime

ClienteForm = db.model_form(Cliente)

ProducaoForm = db.model_form(Producao, field_args={
  'arte_pronta': {'label': 'Arte Pronta?'},
  'impresso': {'label': 'Impresso?'},
  'montado': {'label': 'Montado?'}
})

EntregaForm = db.model_form(Entrega, field_args={
  'enviado': {'label': 'Enviado?'},
  'recebido': {'label': 'Recebido?'}
})

class PedidoForm(Form):
  cliente = fields.ReferencePropertyField(reference_class=Cliente, label_attr='nome', validators=[validators.Required()])
  descricao = TextField('Descricao', [validators.Required()])
  valor = TextField('Valor', [validators.Required()])
  data_entrega = DateField('Data de Entrega', default=datetime.today(), format="%d/%m/%Y")
  pago = BooleanField('Pago?')
  producao = FormField(ProducaoForm, [validators.Required()])
  entrega = FormField(EntregaForm, [validators.Required()])
