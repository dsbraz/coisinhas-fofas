from flask import render_template, request, redirect, url_for, flash, request_started
from models import Cliente, Pedido, Producao, Entrega, cliente_key, pedido_key
from google.appengine.api import users
from microerp import app, usuarios_autorizados
from datetime import datetime

def date_from_str(str_date): return datetime.strptime(str_date, '%d/%m/%Y').date()

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
  if request.method == 'GET':
    cliente = Cliente.get(chave)
    return render_template('editar_cliente.html', cliente=cliente)
  else:
    cliente = Cliente.get(chave)
    cliente.nome = request.form['nome']
    cliente.telefone = request.form['telefone']
    cliente.celular = request.form['celular']
    cliente.email = request.form['email']
    cliente.im = request.form['im']
    cliente.endereco = request.form['endereco']
    cliente.observacao = request.form['observacao']
    cliente.put()
    flash('Cliente alterado com sucesso!')
    return redirect(url_for('listar_clientes'))

@app.route('/cliente/<chave>/excluir', methods=['GET', 'POST'])
def excluir_cliente(chave):
  if request.method == 'GET':
    cliente = Cliente.get(chave)
    return render_template('excluir_cliente.html', cliente=cliente)
  else:
    cliente = Cliente.get(chave)
    if cliente.tem_pedidos():
      flash('Cliente nao pode ser excluido, pois possui pedido(s) associado(s)')
      return render_template('excluir_cliente.html', cliente=cliente)
    cliente.delete()
    flash('Cliente excluido com sucesso!')
    return redirect(url_for('listar_clientes'))

@app.route('/cliente/novo', methods=['GET', 'POST'])
def novo_cliente():
  if request.method == 'GET':
    return render_template('novo_cliente.html')
  else:
    Cliente(
      parent = cliente_key(),
      nome = request.form['nome'],
      telefone = request.form['telefone'],
      celular = request.form['celular'],
      email = request.form['email'],
      im = request.form['im'],
      endereco = request.form['endereco'],
      observacao = request.form['observacao']
    ).put()
    flash('Cliente criado com sucesso!')
    return redirect(url_for('listar_clientes'))

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
  if request.method == 'GET':
    pedido = Pedido.get(chave)
    return render_template('excluir_pedido.html', pedido=pedido)
  else:
    pedido = Pedido.get(chave)
    pedido.producao.delete()
    pedido.entrega.delete()
    pedido.delete()
    flash('Pedido excluido com sucesso!')
    return redirect(url_for('listar_pedidos'))

@app.route('/pedido/<chave>/editar', methods=['GET', 'POST'])
def editar_pedido(chave):
  if request.method == 'GET':
    pedido = Pedido.get(chave)
    clientes_query = Cliente.all().ancestor(cliente_key()).order('nome')
    clientes = clientes_query.run()
    return render_template('editar_pedido.html', pedido=pedido, clientes=clientes)
  else:
    pedido = Pedido.get(chave)
    pedido.cliente = Cliente.get(request.form['cliente'])
    pedido.descricao = request.form['descricao']
    pedido.valor = request.form['valor']
    pedido.data_entrega = date_from_str(request.form['data_entrega'])
    pedido.pago = request.form['pago'] == 'S'
    pedido.put()

    producao = pedido.producao
    producao.arte_pronta = request.form['arte_pronta'] == 'S'
    producao.impresso = request.form['impresso'] == 'S'
    producao.montado = request.form['montado'] == 'S'
    producao.put()

    entrega = pedido.entrega
    entrega.enviado = request.form['enviado'] == 'S'
    entrega.recebido = request.form['recebido'] == 'S'
    entrega.put()

    flash('Pedido alterado com sucesso!')
    return redirect(url_for('listar_pedidos'))

@app.route('/pedido/novo', methods=['GET', 'POST'])
def novo_pedido():
  if request.method == 'GET':
    clientes_query = Cliente.all().ancestor(cliente_key()).order('nome')
    clientes = clientes_query.run()
    return render_template('novo_pedido.html', clientes=clientes)
  else:
    Pedido(
      parent = pedido_key(),
      cliente = Cliente.get(request.form['cliente']),
      descricao = request.form['descricao'],
      valor = request.form['valor'],
      data_entrega = date_from_str(request.form['data_entrega']),
      pago = request.form['pago'] == 'S',
      producao = Producao(
        parent = pedido_key(),
        arte_pronta = request.form['arte_pronta'] == 'S',
        impresso = request.form['impresso'] == 'S',
        montado = request.form['montado'] == 'S'
      ).put(),
      entrega = Entrega(
        parent = pedido_key(),
        enviado = request.form['enviado'] == 'S',
        recebido = request.form['recebido'] == 'S'
      ).put()
    ).put()
    flash('Pedido criado com sucesso!')
    return redirect(url_for('listar_pedidos'))
