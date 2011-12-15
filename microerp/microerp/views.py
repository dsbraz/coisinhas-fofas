from flask import render_template, request, redirect, url_for, flash
from models import Cliente, Pedido, Producao, Entrega, cliente_key, pedido_key
from microerp import app
from datetime import date
import time

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
    pedido.data_entrega = date(*(time.strptime(request.form['data_entrega'], '%d/%M/%Y')[0:3]))
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
      data_entrega = date(*(time.strptime(request.form['data_entrega'], '%d/%M/%Y')[0:3])),
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
