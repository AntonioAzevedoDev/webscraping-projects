BASE_URL = 'http://estatisticas.cetip.com.br/astec/series_v05/paginas/{}'
CETIP_URL = 'http://estatisticas.cetip.com.br/astec/series_v05/paginas/lum_web_v05_series_introducao.asp?str_Modulo=Ativo&int_Idioma=1&int_Titulo=6&int_NivelBD=2'
ATIVOS_URL = {
    'opcoes': 'lum_web_v04_05_ativo.asp?str_Modulo=Ativo&int_Idioma=1&int_Origem=2',
    'estoque': 'lum_web_v04_10_01_estoque.asp?str_Ativo={}&str_TipoInformacao=Estoque&str_TipoInformacaoModelo=0&int_Idioma=1',
    'compromissada': 'lum_web_v04_10_01_estoque.asp?str_Ativo={}&str_TipoInformacao=Negocia%E7%F5es%20Compromissadas&str_TipoInformacaoModelo=0&int_Idioma=1',
    'negocios': 'lum_web_v04_10_01_estoque.asp?str_Ativo={}&str_TipoInformacao=Negocia%E7%F5es%20Definitivas&str_TipoInformacaoModelo=0&int_Idioma=1',
    'volume': 'lum_web_v04_10_01_estoque.asp?str_Ativo={}&str_TipoInformacao=Volume Depositado&str_TipoInformacaoModelo=0&int_Idioma=1'
}
ACT_PATH = r'C:\Users\Lucas Silva\PycharmProjects\webscraping-projects\Cetip\cetip_data\br\actives'
