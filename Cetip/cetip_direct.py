from bs4 import BeautifulSoup
from io import StringIO
from requests import get, post

GERA_URL = 'http://estatisticas.cetip.com.br/astec/series_v05/paginas/lum_web_v04_10_02_gerador_sql.asp'
SQL_URL = 'http://estatisticas.cetip.com.br/astec/series_v05/paginas/lum_web_v04_10_03_consulta.asp'
TESTE = 'http://estatisticas.cetip.com.br/astec/series_v05/paginas/lum_web_v04_05_ativo.asp?str_Modulo=Ativo&int_Idioma=1&int_Origem=2'


r = post(
    SQL_URL,
    data={
        "str_NomeArquivo": "WEB_00_CDB_Estoque_A1",
        "str_NomeTabela": "WEB_CDB_Estoque",
        "str_Ativo": "CDB",
        "str_ModeloDados": "EST_003meta2013",
        "str_Descricao": "_Total",
        "str_NrLeilao": "_Geral",
        "str_ModeloLeilao": "_Geral",
        "str_Descricao_1": "",
        "str_Descricao_2": "",
        "str_Descricao_3": "",
        "chk_Descricao_1": "",
        "chk_Descricao_2": "",
        "chk_Descricao_3": "",
        "bln_MostrarContraparte": "False",
        "str_Populacao": "_Geral",
        "str_FaixaPrazo": "_Geral",
        "str_FaixaPrazoTotalizado": "0",
        "str_TipoFaixaPrazo": "0",
        "str_TipoEmissao": "0",
        "str_Emissao": "_Geral",
        "str_TipoMoeda": "",
        "str_Moeda": "_Geral",
        # "str_Observacao": "Valores Financeiros em Reais.|Do in\xc3\xadcio da s\xc3\xa9rie at\xc3\xa9 30/09/1996 os dados foram transformados| para R$ a partir de uma base em R$ mil.| |Estoque Valorizado.|Metologia de c\xc3\xa1lculo: Pre\xc3\xa7o Unit\xc3\xa1rio da Curva x Quantidade Depositada na data.| |Em caso de M\xc3\xbaltiplas Curvas ou Escalonado, ser\xc3\xa1 considerada a primeira curva informada.",
        "str_Observacao": "",
        "str_NomeAtivoCabecalho": "",
        "str_NomeTipoInformacaoCabecalho": "Estoque",
        "str_TipoDescricao": "0",
        "str_ApresentarTipoOp": "0",
        "dta_DataInicio": "18/10/2022",
        "dta_DataFinal": "19/10/2022",
        "str_SQL": "joao Fdta_DataDivulg, sum(Fdpl_Financeiro) as web_Financeiro maria WEB_CDB_Estoque Group By Fdta_DataDivulg Having ( Fdta_DataDivulg >= #10/19/2022# AND Fdta_DataDivulg <= #10/19/2022# ) ORDER BY Fdta_DataDivulg"
    }
)
print(r.content)

'''
page = BeautifulSoup(get(TESTE).content, 'lxml')
for opt in page.find('select').find_all('option'):
    if '-' in opt.text:
        print(opt['value'], opt.text.split(' - ')[1])
r = post(
    SQL_URL,
    data={
        'DT_DIA_DE': '22',
        'DT_MES_DE': '04',
        'DT_ANO_DE': '2022',
        'DT_DIA_ATE': '19',
        'DT_MES_ATE': '10',
        'DT_ANO_ATE': '2022',
        'str_NomeArquivo': 'WEB_00_CDB_Estoque_A1',
        'str_NomeTabela': 'WEB_CDB_Estoque',
        'str_Ativo': 'CDB',
        'str_TipoDescricao': '0',
        'str_TipoFaixaPrazo': '0',
        'str_ModeloDados': 'EST_003meta2013',
        'str_TipoEmissao': '0',
        'str_TipoMoeda': '',
        'str_Descricao': '_Geral',
        'str_Populacao': '_Geral',
        'str_FaixaPrazo': '_Geral',
        'str_NrLeilao': '_Geral',
        'str_ModeloLeilao': '_Geral',
        'str_FaixaPrazoTotalizado': '0',
        'str_Emissao': '_Geral',
        'str_Moeda': '_Geral',
        'str_ApresentarTipoOp': '0',
        'str_Observacao': 'Valores Financeiros em Reais.|Do início da série até 30/09/1996 os dados foram transformados| para R$ a partir de uma base em R$ mil.| |Estoque Valorizado.|Metologia de cálculo: Preço Unitário da Curva x Quantidade Depositada na data.| |Em caso de Múltiplas Curvas ou Escalonado, será considerada a primeira curva informada.',
        'str_NomeAtivoCabecalho': 'CDB - Certificado de Depósito Bancário',
        'str_NomeTipoInformacaoCabecalho': 'Estoque',
        'int_Idioma': '1'
    }
)
print(r.content)
'''