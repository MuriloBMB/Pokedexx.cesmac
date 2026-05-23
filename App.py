from flask import Flask, request, redirect, render_template, session
import json
import random
import os

app = Flask(__name__)
app.secret_key = 'pokemon123'

ARQUIVO_USERS = 'user.json'
ARQUIVO_POKEMON = 'pokemom.json'


# ================= FUNÇÕES ====================

def carregar_usuarios():
    if not os.path.exists(ARQUIVO_USERS):
        return []

    with open(ARQUIVO_USERS, 'r', encoding='utf-8') as arquivo:
        try:
            return json.load(arquivo)
        except:
            return []


def salvar_usuarios(usuarios):
    with open(ARQUIVO_USERS, 'w', encoding='utf-8') as arquivo:
        json.dump(usuarios, arquivo, indent=4, ensure_ascii=False)


# ================== HOME ====================

@app.route('/')
def main():

    if 'usuario' not in session:
        return redirect('/login')

    with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as arquivo:
        pokemom = json.load(arquivo)

    return render_template('main.html', pokemom=pokemom)


# ================= CADASTRO =================

@app.route('/cadastrouser')
def cadastro_page():
    return render_template('cadastrouser.html')

@app.route('/cadastrouser', methods=['POST'])
def cadastro():

    nome = request.form['Nome']
    user = request.form['User']
    senha = request.form['Senha']

    if not user or not senha:
        return render_template(
            'cadastrouser.html',
            erro="Prencha todos os campos"
        )

    usuarios = carregar_usuarios()

    for usuario in usuarios:
        if user.lower() == usuario['user'].lower():
            return render_template(
                'cadastrouser.html',
                erro="Usuário já existe!"
            )

    novo_usuario = {
        "id": len(usuarios) + 1,
        "nome": nome,
        "user": user,
        "senha": senha,
        "pokemons": []
    }

    usuarios.append(novo_usuario)

    salvar_usuarios(usuarios)

    return redirect('/login')


# ================= LOGIN/LOGOUT =================

@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():

    user = request.form['User']
    senha = request.form['Senha']

    if not user or not senha:
        return render_template(
            'login.html',
            erro="Prencha todos os campos"
        )

    usuarios = carregar_usuarios()

    for usuario in usuarios:

        if (
            user.lower() == usuario['user'].lower()
            and senha == usuario['senha']
        ):

            session['usuario'] = usuario['user']

            return redirect('/')

    return render_template(
        'login.html',
        erro="Usuário ou senha incorretos"
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ================= UNÇÃO STATUS =================
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
        "media_speed": media_speed
    }


#================ POKEDEX =====================

@app.route('/pokedex')
def pokedex_page():

    if 'usuario' not in session:
        return redirect('/login')

    usuarios = carregar_usuarios()

    with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as arquivo:
        todos_pokemons = json.load(arquivo)

    pokemom_sorteado = []

    for usuario in usuarios:

        if usuario['user'] == session['usuario']:

            ids_salvos = usuario.get('pokemons', [])

            for pokemon in todos_pokemons:

                if pokemon['id'] in ids_salvos:
                    pokemom_sorteado.append(pokemon)

    status = calcular_status(pokemom_sorteado)

    return render_template(
        'pokedex.html',

        pokemom_sorteado=pokemom_sorteado,

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
        media_speed=status['media_speed']
    )


@app.route('/sortear')
def sortear():

    if 'usuario' not in session:
        return redirect('/login')

    usuarios = carregar_usuarios()

    usuario_logado = None

    for usuario in usuarios:

        if usuario['user'] == session['usuario']:
            usuario_logado = usuario
            break

    # impede novo sorteio
    if usuario_logado.get('pokemons'):

        with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as arquivo:
            todos_pokemons = json.load(arquivo)

        pokemom_sorteado = []

        for pokemon in todos_pokemons:

            if pokemon['id'] in usuario_logado['pokemons']:
                pokemom_sorteado.append(pokemon)

        status = calcular_status(pokemom_sorteado)

        return render_template(
            'pokedex.html',

            pokemom_sorteado=pokemom_sorteado,

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

            erro="Você já sorteou seus pokémons!"
        )

    with open(ARQUIVO_POKEMON, 'r', encoding='utf-8') as arquivo:
        pokemom = json.load(arquivo)

    pokemom_sorteado = random.sample(pokemom, 6)

    ids_pokemom = []

    for pokemon in pokemom_sorteado:
        ids_pokemom.append(pokemon["id"])

    usuario_logado['pokemons'] = ids_pokemom

    salvar_usuarios(usuarios)

    status = calcular_status(pokemom_sorteado)

    return render_template(
        'pokedex.html',

        pokemom_sorteado=pokemom_sorteado,

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
        media_speed=status['media_speed']
    )
# ================= RUN =================

if __name__ == '__main__':
    app.run(debug=True)