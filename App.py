from flask import Flask, request, redirect, render_template, session  # type: ignore[import]
import json
import random

app = Flask(__name__)
app.secret_key = 'pokemon123'

ARQUIVO_USERS = 'user.json'
ARQUIVO_POKEMON = 'pokemon.json'


def carregar_usuarios():
    try:
        with open(ARQUIVO_USERS, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def salvar_usuarios(usuarios):
    with open(ARQUIVO_USERS, 'w', encoding='utf-8') as f:
        json.dump(usuarios, f, indent=4, ensure_ascii=False)


def carregar_pokemons():
    try:
        with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def calcular_status(pokemons):
    total_hp = 0
    total_attack = 0
    total_defense = 0
    total_sp_attack = 0
    total_sp_defense = 0
    total_speed = 0

    for pokemon in pokemons:
        total_hp += pokemon['base']['HP']
        total_attack += pokemon['base']['Attack']
        total_defense += pokemon['base']['Defense']
        total_sp_attack += pokemon['base']['Sp. Attack']
        total_sp_defense += pokemon['base']['Sp. Defense']
        total_speed += pokemon['base']['Speed']

    quantidade = len(pokemons)

    if quantidade > 0:
        media_hp = total_hp // quantidade
        media_attack = total_attack // quantidade
        media_defense = total_defense // quantidade
        media_sp_attack = total_sp_attack // quantidade
        media_sp_defense = total_sp_defense // quantidade
        media_speed = total_speed // quantidade
    else:
        media_hp = 0
        media_attack = 0
        media_defense = 0
        media_sp_attack = 0
        media_sp_defense = 0
        media_speed = 0

    return {
        "total_hp": total_hp,
        "total_attack": total_attack,
        "total_defense": total_defense,
        "total_sp_attack": total_sp_attack,
        "total_sp_defense": total_sp_defense,
        "total_speed": total_speed,
        "media_hp": media_hp,
        "media_attack": media_attack,
        "media_defense": media_defense,
        "media_sp_attack": media_sp_attack,
        "media_sp_defense": media_sp_defense,
        "media_speed": media_speed,
    }


@app.route('/')
def home():
    if 'usuario' not in session:
        return redirect('/login')
    pokemons = carregar_pokemons()
    return render_template('main.html', pokemons=pokemons)


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

    todos_os_pokemons = carregar_pokemons()
    pokemons_por_id = {}
    for p in todos_os_pokemons:
        pokemons_por_id[p['id']] = p

    usuarios = carregar_usuarios()
    ids_do_usuario = []
    for u in usuarios:
        if u['user'] == session['usuario']:
            ids_do_usuario = u.get('pokemons', [])
            break

    pokemons = []
    for id_pokemon in ids_do_usuario:
        if id_pokemon in pokemons_por_id:
            pokemons.append(pokemons_por_id[id_pokemon])

    status = calcular_status(pokemons)
    erro = session.pop('erro', None)

    return render_template(
        'pokedex.html',
        pokemons=pokemons,
        erro=erro,
        total_hp=status['total_hp'],
        total_attack=status['total_attack'],
        total_defense=status['total_defense'],
        total_sp_attack=status['total_sp_attack'],
        total_sp_defense=status['total_sp_defense'],
        total_speed=status['total_speed'],
        media_hp=status['media_hp'],
        media_attack=status['media_attack'],
        media_defense=status['media_defense'],
        media_sp_attack=status['media_sp_attack'],
        media_sp_defense=status['media_sp_defense'],
        media_speed=status['media_speed'],
    )


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

    if usuario_logado is None:
        return redirect('/login')

    if usuario_logado.get('pokemons'):
        session['erro'] = "Você já sorteou seus pokémons!"
        return redirect('/pokedex')

    todos_os_pokemons = carregar_pokemons()
    pokemons_sorteados = random.sample(todos_os_pokemons, 6)

    ids_sorteados = []
    for pokemon in pokemons_sorteados:
        ids_sorteados.append(pokemon['id'])

    usuario_logado['pokemons'] = ids_sorteados
    salvar_usuarios(usuarios)

    return redirect('/pokedex')


@app.route('/comparar')
def comparar():
    if 'usuario' not in session:
        return redirect('/login')

    todos_os_pokemons = carregar_pokemons()
    pokemons_por_id = {}
    for p in todos_os_pokemons:
        pokemons_por_id[p['id']] = p

    usuarios = carregar_usuarios()
    times = []
    for u in usuarios:
        ids = u.get('pokemons', [])
        pokemons_do_time = []
        for id_pokemon in ids:
            if id_pokemon in pokemons_por_id:
                pokemons_do_time.append(pokemons_por_id[id_pokemon])

        if len(pokemons_do_time) == 0:
            continue

        status = calcular_status(pokemons_do_time)
        times.append({
            'nome': u['nome'],
            'user': u['user'],
            'pokemons': pokemons_do_time,
            'status': status,
        })

    return render_template('comparar.html', times=times, usuario_logado=session['usuario'])


if __name__ == '__main__':
    app.run(debug=False)
