from flask import render_template, request, redirect, url_for, flash, request_started
from models import Cliente, Pedido, Producao, Entrega, cliente_key, pedido_key
from forms import ClienteForm, PedidoForm
from google.appengine.api import users
from microerp import app, usuarios_autorizados
from datetime import datetime

@app.template_filter('format_date')
def format_date(d): return d.strftime("%d/%m/%Y")

@app.before_request
def authorize():
  user = users.get_current_user()
  if not user or user.email() not in usuarios_autorizados: raise Exception('Usuario invalido')

@app.errorhandler(404)
def page_not_found(e): return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e): return render_template('500.html'), 500

@app.route('/', methods=['GET'])
def index(): return render_template('index.html')

@app.route('/cliente', methods=['GET'])
def listar_clientes():
  clientes_query = Cliente.all().ancestor(cliente_key()).order('nome')
  clientes = clientes_query.run()
  return render_template('listar_clientes.html', clientes=clientes)

@app.route('/cliente/<chave>', methods=['GET'])
def detalhar_cliente(chave):
  cliente = Cliente.get(chave)
  return render_template('detalhar_cliente.html', cliente=cliente)

@app.route('/cliente/<chave>/editar', methods=['GET', 'POST'])
def editar_cliente(chave):
  cliente = Cliente.get(chave)
  form = ClienteForm(request.form, cliente)
  if request.method == 'POST' and form.validate():
    form.populate_obj(cliente)
    cliente.put()
    flash('Cliente alterado com sucesso!')
    return redirect(url_for('listar_clientes'))
  return render_template('editar_cliente.html', chave=chave, form=form)

@app.route('/cliente/<chave>/excluir', methods=['GET', 'POST'])
def excluir_cliente(chave):
  cliente = Cliente.get(chave)
  if request.method == 'POST':
    if not cliente.tem_pedidos():
      cliente.delete()
      flash('Cliente excluido com sucesso!')
      return redirect(url_for('listar_clientes'))
    flash('Cliente nao pode ser excluido, pois possui pedido(s) associado(s)')
  return render_template('excluir_cliente.html', cliente=cliente)

@app.route('/cliente/novo', methods=['GET', 'POST'])
def novo_cliente():
  form = ClienteForm(request.form)
  if request.method == 'POST' and form.validate():
    Cliente(
      parent = cliente_key(),
      nome = form.nome.data,
      telefone = form.telefone.data,
      celular = form.celular.data,
      email = form.email.data,
      im = form.im.data,
      endereco = form.endereco.data,
      observacao = form.observacao.data
    ).put()
    flash('Cliente criado com sucesso!')
    return redirect(url_for('listar_clientes'))
  return render_template('novo_cliente.html', form=form)

@app.route('/pedido', methods=['GET'])
def listar_pedidos():
  pedidos_query = Pedido.all().ancestor(pedido_key()).order('data_entrega')
  pedidos = pedidos_query.run()
  return render_template('listar_pedidos.html', pedidos=pedidos)

@app.route('/pedido/<chave>', methods=['GET'])
def detalhar_pedido(chave):
  pedido = Pedido.get(chave)
  return render_template('detalhar_pedido.html', pedido=pedido)

@app.route('/pedido/<chave>/excluir', methods=['GET', 'POST'])
def excluir_pedido(chave):
  pedido = Pedido.get(chave)
  if request.method == 'POST':
    pedido = Pedido.get(chave)
    pedido.producao.delete()
    pedido.entrega.delete()
    pedido.delete()
    flash('Pedido excluido com sucesso!')
    return redirect(url_for('listar_pedidos'))
  return render_template('excluir_pedido.html', pedido=pedido)

@app.route('/pedido/<chave>/editar', methods=['GET', 'POST'])
def editar_pedido(chave):
  pedido = Pedido.get(chave)
  form = PedidoForm(request.form, pedido)
  if request.method == 'POST' and form.validate():
    form.populate_obj(pedido)
    pedido.producao.put()
    pedido.entrega.put()
    pedido.put()
    flash('Pedido alterado com sucesso!')
    return redirect(url_for('listar_pedidos'))
  return render_template('editar_pedido.html', chave=chave, form=form)

@app.route('/pedido/novo', methods=['GET', 'POST'])
def novo_pedido():
  form = PedidoForm(request.form)
  if request.method == 'POST' and form.validate():
    Pedido(
      parent = pedido_key(),
      cliente = form.cliente.data,
      descricao = form.descricao.data,
      valor = form.valor.data,
      data_entrega = form.data_entrega.data,
      pago = form.pago.data,
      producao = Producao(
        parent = pedido_key(),
        arte_pronta = form.producao.arte_pronta.data,
        impresso = form.producao.impresso.data,
        montado = form.producao.montado.data
      ).put(),
      entrega = Entrega(
        parent = pedido_key(),
        enviado = form.entrega.enviado.data,
        recebido = form.entrega.recebido.data
      ).put()
    ).put()
    flash('Pedido criado com sucesso!')
    return redirect(url_for('listar_pedidos'))
  return render_template('novo_pedido.html', form=form)
