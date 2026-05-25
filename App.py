from flask import Flask, request, redirect, render_template, session
import json
import random

app = Flask(__name__)
app.secret_key = 'pokemon123'

ARQUIVO_USERS = 'user.json'
ARQUIVO_POKEMON = 'pokemom.json'


def carregar_usuarios():
    try:
        with open(ARQUIVO_USERS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def salvar_usuarios(usuarios):
    with open(ARQUIVO_USERS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)


CHAVES = ['HP', 'Attack', 'Defense', 'Sp. Attack', 'Sp. Defense', 'Speed']
PREFIXOS = ['hp', 'attack', 'defense', 'sp_attack', 'sp_defense', 'speed']


def calcular_status(pokemons):
    totais = dict.fromkeys(PREFIXOS, 0)
    for pk in pokemons:
        for chave, pref in zip(CHAVES, PREFIXOS):
            totais[pref] += pk['base'][chave]
    qtd = len(pokemons)
    out = {}
    for pref in PREFIXOS:
        out[f'total_{pref}'] = totais[pref]
        out[f'media_{pref}'] = totais[pref] // qtd if qtd > 0 else 0
    return out


@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect('/login')
    with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as f:
        pokemons = json.load(f)
    return render_template('main.html', pokemom=pokemons)


@app.route('/cadastrouser', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'GET':
        return render_template('cadastrouser.html')

    nome = request.form['Nome']
    user = request.form['User']
    senha = request.form['Senha']

    if not user or not senha:
        return render_template('cadastrouser.html', erro="Preencha todos os campos")

    usuarios = carregar_usuarios()
    for u in usuarios:
        if user.lower() == u['user'].lower():
            return render_template('cadastrouser.html', erro="Usuário já existe!")

    usuarios.append({
        "id": len(usuarios) + 1,
        "nome": nome, "user": user,
        "senha": senha, "pokemons": []
    })
    salvar_usuarios(usuarios)
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    user = request.form['User']
    senha = request.form['Senha']

    if not user or not senha:
        return render_template('login.html', erro="Preencha todos os campos")

    for u in carregar_usuarios():
        if user.lower() == u['user'].lower() and senha == u['senha']:
            session['usuario'] = u['user']
            return redirect('/')

    return render_template('login.html', erro="Usuário ou senha incorretos")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@app.route('/pokedex')
def pokedex():
    if 'usuario' not in session:
        return redirect('/login')

    with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as f:
        todos = json.load(f)
    por_id = {p['id']: p for p in todos}

    ids = []
    for u in carregar_usuarios():
        if u['user'] == session['usuario']:
            ids = u.get('pokemons', [])
            break

    pokemons = [por_id[i] for i in ids if i in por_id]
    status = calcular_status(pokemons)
    erro = session.pop('erro', None)

    return render_template('pokedex.html', pokemom_sorteado=pokemons, erro=erro, **status)


@app.route('/sortear')
def sortear():
    if 'usuario' not in session:
        return redirect('/login')

    usuarios = carregar_usuarios()
    usuario_logado = None
    for u in usuarios:
        if u['user'] == session['usuario']:
            usuario_logado = u
            break

    if usuario_logado.get('pokemons'):
        session['erro'] = "Você já sorteou seus pokémons!"
        return redirect('/pokedex')

    with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as f:
        todos = json.load(f)

    sorteados = random.sample(todos, 6)
    usuario_logado['pokemons'] = [p['id'] for p in sorteados]
    salvar_usuarios(usuarios)

    return render_template('pokedex.html', pokemom_sorteado=sorteados, **calcular_status(sorteados))


if __name__ == '__main__':
    app.run(debug=False)
