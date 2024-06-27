import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
  stats = {}
  stats = db.execute('''
    SELECT * FROM
      (SELECT COUNT(*) n_Pilotos FROM Pilotos)
    JOIN
      (SELECT COUNT(*) n_Nacionalidades FROM (SELECT distinct p.pais FROM Pilotos p))
    JOIN
      (SELECT COUNT(*) n_Equipas FROM Equipas)
    JOIN
      (select max(nr) as maximo
          from(
          select nomePiloto,count(*) nr 
          from resultadosfinais
          where posicaofinal=1
          group by nomePiloto))
    JOIN
      (SELECT COUNT(*) n_Corridas FROM Corridas)
    JOIN 
      (SELECT COUNT(*) n_Paises FROM (SELECT distinct circuitos.pais FROM Circuitos)
    )
   
    ''').fetchone()
  logging.info(stats)
  return render_template('index.html',stats=stats)

# Pilotos
@APP.route('/pilotos/')
def list_pilotos():
    pilotos = db.execute(
      '''
      SELECT numPiloto, nomePiloto, nome_equipa,pais 
      FROM Pilotos
      ORDER BY numPiloto
      ''').fetchall()
    return render_template('pilotos-list.html', pilotos=pilotos)


@APP.route('/pilotos/search/<expr>/')
def search_piloto(expr):
  search = { 'expr': expr }
  pilotos2 = db.execute(
      ' SELECT nomePiloto'
      ' FROM Pilotos '
      ' WHERE nomePiloto LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('pilotos-search.html', 
           search=search,pilotos2=pilotos2)


@APP.route('/pilotos/<expr>/')
def get_piloto(expr):
  search = { 'expr': expr }
  expr= '%' + expr + '%'
  piloto = db.execute(
      '''
      SELECT numPiloto, nomePiloto, nome_equipa, pais, data_nascimento,motor, 
      nome_chassi, pontos_finais
      FROM Pilotos
      WHERE nomePiloto like ?
      ''', [expr]).fetchone()

  equipa = db.execute(
      '''
      SELECT nome_equipa 
      FROM Pilotos
      WHERE nomePiloto like ?
      ''', [expr]).fetchall()

  colega = db.execute(
      '''
      SELECT nomePiloto
      FROM pilotos
      WHERE pilotos.nome_equipa=(SELECT nome_equipa 
      FROM Pilotos
      WHERE pilotos.nomePiloto like ?)
      ''', [expr]).fetchall()
  
  part = db.execute(
    '''
    select corridas.nomeCorrida as corrida,qualificações.nomePiloto, qualificações.posicao as quali, resultadosfinais.posicaoFinal, resultadosfinais.tempoFinal, 
    resultadosfinais.tempoFinal, resultadosfinais.pontosGanhos
      from Qualificações join ResultadosFinais on qualificações.nomeCorrida=ResultadosFinais.nomeCorrida 
      and resultadosfinais.nomePiloto=qualificações.nomePiloto
      join corridas on corridas.pais= resultadosfinais.nomeCorrida
    where qualificações.nomePiloto like ?
    order by corrida
    ''',[expr]
    ).fetchall()
  

  
  return render_template('piloto.html', 
           piloto=piloto, equipa=equipa, colega=colega, part=part)



# Equipas
@APP.route('/equipas/')
def list_equipas():
    equipas = db.execute('''
      SELECT nomeEquipa, pais_origem, chefe, motor, num_campeonatos
      FROM Equipas
      ORDER BY nomeEquipa
    ''').fetchall()
    return render_template('equipas-list.html', equipas=equipas)

@APP.route('/equipas/search/<expr>/')
def search_equipas(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  equipas = db.execute(
      ' SELECT nomeEquipa'
      ' FROM Equipas '
      ' WHERE nomeEquipa LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('equipas-search.html', 
           search=search,equipas=equipas)

@APP.route('/equipas/<expr>/')
def verequipas(expr):
  search = { 'expr': expr }
  expr= '%' + expr + '%'
  dados = db.execute(
    '''
    SELECT nomePiloto,nomeEquipa, pais_origem, e.motor, chefe, num_campeonatos
    FROM Equipas e join Pilotos on pilotos.nome_equipa=e.nomeEquipa
    WHERE nomeEquipa like ?
    ''', [expr]).fetchone()
  
  pilequipas = db.execute(
    '''
    SELECT nomePiloto,nomeEquipa, pais_origem, e.motor, chefe, num_campeonatos
    FROM Equipas e join Pilotos on pilotos.nome_equipa=e.nomeEquipa
    WHERE nomeEquipa like ?
    ''', [expr]).fetchall()

  if expr is None:
     abort(404, 'Equipa nome {} does not exist.'.format(expr))

  
  return render_template('equipas.html', 
           pilequipas=pilequipas, dados=dados)
# Corridas
@APP.route('/corridas/')
def list_corridas():
    corridas = db.execute('''
      SELECT nomeCorrida
      FROM Corridas
      ORDER BY nomeCorrida
    ''').fetchall()
    return render_template('corridas-list.html', corridas=corridas)

@APP.route('/corridas/search/<expr>/')
def search_corridas(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  corridas2 = db.execute(
      ' SELECT nomeCorrida'
      ' FROM Corridas '
      ' WHERE nomeCorrida LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('corridas-search.html', 
           search=search,corridas2=corridas2)

@APP.route('/corridas/<expr>/')
def view_corridas_by_name(expr):
  search = { 'expr': expr }
  expr= '%' + expr + '%'
  corrida = db.execute(
    '''
    SELECT corridas.nomeCorrida, circuitos.nomeCircuito,data,num_voltas,distancia,corridas.pais, num_zonas_drs as drs, circuitos.recorde_volta
    FROM Corridas 
    join circuitos on circuitos.pais=corridas.pais
    WHERE nomeCorrida LIKE ?
    ''',[expr]
    ).fetchone()

  if corrida is None:
     abort(404, 'Nome da Corrida {} não existe.'.format(expr))

  correu = db.execute(
    '''
    SELECT nomePiloto,tempoFinal
    FROM(
      SELECT *
      FROM Corridas join ResultadosFinais on Corridas.pais = ResultadosFinais.nomeCorrida
      WHERE ResultadosFinais.posicaoFinal= 1)
    WHERE nomeCorrida= ?
    ''',[expr]
    ).fetchall()
 

  return render_template('corridas.html', 
           corrida=corrida,correu=correu)

#Resultados
@APP.route('/resultados/<expr>/')
def resultado(expr):
  search = { 'expr': expr }
  expr= '%' + expr + '%'
  resultados = db.execute(
    '''
    select corridas.nomeCorrida as corrida,qualificações.nomePiloto, qualificações.posicao as quali, resultadosfinais.posicaoFinal, resultadosfinais.tempoFinal, resultadosfinais.pontosGanhos
      from Qualificações join ResultadosFinais on qualificações.nomeCorrida=ResultadosFinais.nomeCorrida 
      and resultadosfinais.nomePiloto=qualificações.nomePiloto
      join corridas on corridas.pais= resultadosfinais.nomeCorrida
    where corrida like ?
    order by posicaoFinal
    ''',[expr]
    ).fetchall()
  
  if resultados is None:
     abort(404, 'Não existem Resultados'.format(expr))
  
  return render_template('resultados.html', 
           resultados=resultados)

