import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import streamlit as st
import plotly.graph_objs as go

#Por utilizar o skfuzzy, o método de defuzzificação empregado é o do Centro de Gravidade


st.set_page_config(page_title='Controle de Ultrapassagem de Veículo Autônomo', layout='wide')

# Erros na inferência
def safe_compute(simulation):
    try:
        simulation.compute()
        return True
    except Exception as e:
        st.error(f"Erro ao calcular a saída: {e}")
        return False

# Preparação para plotar as funções de pertinência
def get_fuzzy_label(var, value):
    pertinencias = {label: fuzz.interp_membership(var.universe, var[label].mf, value) for label in var.terms}
    label = max(pertinencias, key=pertinencias.get)  
    return label, pertinencias[label]

# Variáveis linguísticas

# Distância (0 a 500 metros)
distancia = ctrl.Antecedent(np.arange(0, 501, 1), 'distancia')
distancia['muito_curta'] = fuzz.trapmf(distancia.universe, [0, 0, 100, 200])
distancia['adequada'] = fuzz.trimf(distancia.universe, [150, 250, 350])
distancia['muito_longa'] = fuzz.trapmf(distancia.universe, [300, 400, 500, 500])

# Permissão (0 a 1)
permissao = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'permissao')
permissao['proibido'] = fuzz.trapmf(permissao.universe, [0, 0, 0.2, 0.4])
permissao['permitido'] = fuzz.trimf(permissao.universe, [0.3, 0.6, 1])

# Pista (0 a 1)
pista = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'pista')
pista['obstruida'] = fuzz.trapmf(pista.universe, [0, 0, 0.3, 0.5])
pista['livre'] = fuzz.trimf(pista.universe, [0.4, 0.7, 1])

# Velocidade (0 a 100 km/h)
velocidade = ctrl.Antecedent(np.arange(0, 101, 1), 'velocidade')
velocidade['baixa'] = fuzz.trapmf(velocidade.universe, [0, 0, 30, 50])
velocidade['adequada'] = fuzz.trimf(velocidade.universe, [40, 60, 80])
velocidade['alta'] = fuzz.trapmf(velocidade.universe, [70, 90, 100, 100])

# Visibilidade (0 a 1)
visibilidade = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'visibilidade')
visibilidade['ruim'] = fuzz.trapmf(visibilidade.universe, [0, 0, 0.2, 0.5])
visibilidade['boa'] = fuzz.trimf(visibilidade.universe, [0.4, 0.7, 1])

# Lombada (0 a 1)
lombada = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'lombada')
lombada['presente'] = fuzz.trapmf(lombada.universe, [ 0.5, 0.6, 1, 1])
lombada['ausente'] = fuzz.trapmf(lombada.universe, [ 0, 0, 0.5, 0.6])

# Cruzamento (0 a 1)
cruzamento = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'cruzamento')
cruzamento['presente'] = fuzz.trapmf(cruzamento.universe, [ 0.4, 0.5, 1, 1])
cruzamento['ausente'] = fuzz.trapmf(cruzamento.universe, [ 0, 0, 0.4, 0.5])

# Passagem de nível (0 a 1)
passagem_nivel = ctrl.Antecedent(np.arange(0, 1.1, 0.1), 'passagem_nivel')
passagem_nivel['presente'] = fuzz.trapmf(passagem_nivel.universe, [ 0.7, 0.8, 1, 1])
passagem_nivel['ausente'] = fuzz.trapmf(passagem_nivel.universe, [ 0, 0, 0.7, 0.8])

# Variável de saída: Decisão de ultrapassagem (0 a 1)
ultrapassagem = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'ultrapassagem')
ultrapassagem['nao'] = fuzz.trapmf(ultrapassagem.universe, [0, 0, 0.2, 0.5])
ultrapassagem['sim'] = fuzz.trimf(ultrapassagem.universe, [0.4, 0.7, 1])

# Regras de inferência
rule1 = ctrl.Rule(distancia['adequada'] & permissao['permitido'] & pista['livre'] & velocidade['adequada'] & visibilidade['boa'] & lombada['ausente'] & cruzamento['ausente'] & passagem_nivel['ausente'], ultrapassagem['sim'])
rule2 = ctrl.Rule(distancia['muito_longa'] | velocidade['baixa'] | permissao['proibido'] | pista['obstruida'] | visibilidade['ruim'] | lombada['presente'] | cruzamento['presente'] | passagem_nivel['presente'], ultrapassagem['nao'])
rule3 = ctrl.Rule(velocidade['alta'], ultrapassagem['sim'])
rule4 = ctrl.Rule(distancia['muito_curta'] & pista['livre'], ultrapassagem['sim'])


# Regras do sistema de controle
sistema = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
simulacao = ctrl.ControlSystemSimulation(sistema)

# Interface com Streamlit
st.title('Sistema de Controle de Ultrapassagem de Veículo Autônomo')

# Sliders para entrada de dados
distancia_input = st.slider('Distância (0 a 500 metros)', 0, 500, 250, step=1)
label_distancia, pertinencia_distancia = get_fuzzy_label(distancia, distancia_input)
st.write(f'Distância: {label_distancia} ({pertinencia_distancia:.2f})')

permissao_input = st.slider('Permissão de Ultrapassagem (0.0 a 1.0)', 0.0, 1.0, 0.5, step=0.1)
label_permissao, pertinencia_permissao = get_fuzzy_label(permissao, permissao_input)
st.write(f'Permissão: {label_permissao} ({pertinencia_permissao:.2f})')

pista_input = st.slider('Condição da Pista (0.0 a 1.0)', 0.0, 1.0, 0.5, step=0.1)
label_pista, pertinencia_pista = get_fuzzy_label(pista, pista_input)
st.write(f'Pista: {label_pista} ({pertinencia_pista:.2f})')

velocidade_input = st.slider('Velocidade (0 a 100 km/h)', 0, 100, 60, step=1)
label_velocidade, pertinencia_velocidade = get_fuzzy_label(velocidade, velocidade_input)
st.write(f'Velocidade: {label_velocidade} ({pertinencia_velocidade:.2f})')

visibilidade_input = st.slider('Visibilidade (0.0 a 1.0)', 0.0, 1.0, 0.5, step=0.1)
label_visibilidade, pertinencia_visibilidade = get_fuzzy_label(visibilidade, visibilidade_input)
st.write(f'Visibilidade: {label_visibilidade} ({pertinencia_visibilidade:.2f})')

lombada_input = st.slider('Lombada (0 = Ausente, 1 = Presente)', 0.0, 1.0, 0.0, step=0.1)
label_lombada, pertinencia_lombada = get_fuzzy_label(lombada, lombada_input)
st.write(f'Lombada: {label_lombada} ({pertinencia_lombada:.2f})')

cruzamento_input = st.slider('Cruzamento (0 = Ausente, 1 = Presente)', 0.0, 1.0, 0.0, step=0.1)
label_cruzamento, pertinencia_cruzamento = get_fuzzy_label(cruzamento, cruzamento_input)
st.write(f'Cruzamento: {label_cruzamento} ({pertinencia_cruzamento:.2f})')

passagem_nivel_input = st.slider('Passagem de Nível (0 = Ausente, 1 = Presente)', 0.0, 1.0, 0.0, step=0.1)
label_passagem_nivel, pertinencia_passagem_nivel = get_fuzzy_label(passagem_nivel, passagem_nivel_input)
st.write(f'Passagem de Nível: {label_passagem_nivel} ({pertinencia_passagem_nivel:.2f})')


# Passando entradas para a simulação
simulacao.input['distancia'] = distancia_input
simulacao.input['permissao'] = permissao_input
simulacao.input['pista'] = pista_input
simulacao.input['velocidade'] = velocidade_input
simulacao.input['visibilidade'] = visibilidade_input
simulacao.input['lombada'] = lombada_input
simulacao.input['cruzamento'] = cruzamento_input
simulacao.input['passagem_nivel'] = passagem_nivel_input

# Computação do sistema
if safe_compute(simulacao):
    resultado = simulacao.output["ultrapassagem"]
    st.write(f'Decisão de Ultrapassagem: {resultado:.2f}')
    
    # Exibindo se a ultrapassagem é permitida ou não
    if resultado >= 0.5:
        st.success('Ultrapassagem permitida')
    else:
        st.error('Ultrapassagem não permitida')

# Função para exibir gráficos das funções de pertinência
def plot_fuzzy_var(var, var_name, input_value=None):
    traces = []
    for label in var.terms:
        trace = go.Scatter(
            x=var.universe,
            y=var[label].mf,
            mode='lines',
            name=label
        )
        traces.append(trace)

    layout = go.Layout(title=f'Função de Pertinência - {var_name}', xaxis=dict(title=var_name), yaxis=dict(title='Pertinência'))
    fig = go.Figure(data=traces, layout=layout)

    if input_value is not None:
        fig.add_shape(go.layout.Shape(type="line", x0=input_value, y0=0, x1=input_value, y1=1, line=dict(color="Red", dash="dashdot")))
    
    return fig

# Exibição dos gráficos
st.plotly_chart(plot_fuzzy_var(distancia, 'Distância', input_value=distancia_input))
st.plotly_chart(plot_fuzzy_var(permissao, 'Permissão', input_value=permissao_input))
st.plotly_chart(plot_fuzzy_var(pista, 'Pista', input_value=pista_input))
st.plotly_chart(plot_fuzzy_var(velocidade, 'Velocidade', input_value=velocidade_input))
st.plotly_chart(plot_fuzzy_var(visibilidade, 'Visibilidade', input_value=visibilidade_input))
st.plotly_chart(plot_fuzzy_var(lombada, 'Lombada', input_value=lombada_input))
st.plotly_chart(plot_fuzzy_var(cruzamento, 'Cruzamento', input_value=cruzamento_input))
st.plotly_chart(plot_fuzzy_var(passagem_nivel, 'Passagem de Nível', input_value=passagem_nivel_input))