 # Arquivando Valores das Variaáveis
def result_table (name, address, number, comments):
    result_dic = {
        "Resultado": name,
        "Endereço": address,
        "Telefone": number,
        "Observações": comments,
    }
    return result_dic

 # Imports para o Projeto
from django.shortcuts import render
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import pandas as pd

# Rendenizando página HomePage
def homepage(request):
    return render(request, 'homepage.html')

 # Rendenizando página Search_Page
def search(request):
    return render(request, 'search_page.html')

def select_all(result_dic):
    contact = []
    checkbox_all = True
    html_checkbox = '<input type="checkbox">'
    javascript_code = """
       <script>
       function alterarCheckbox() {
           var checkbox = document.getElementById('checkbox');
           checkbox_all = checkbox.checked;
       }
       </script>
       """
    if checkbox_all == True:
        contact += result_dic[2]
    elif():
        pass
    return html_checkbox + javascript_code


  # Coletando Informações e Apresentando em Tabela
def all_results(request):
    county = request.POST.get('municipio')
    new_county = county.replace(' ', '+')
    local = request.POST.get('local')
    new_local = local.replace(' ', '+')

    # Configuração do Serviço e do Driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(2)

    # Criando Listas Vazias para Incluir Valores
    name = []
    address = []
    number = []
    comments = []

    url = 'https://www.google.com.br/maps/search/{}+{}/@-24.0416944,-46.5883118,12z/data=!3m1!4b1?entry=ttu'.format(new_local, new_county)

    # Abrindo a URL
    driver.get(url)

    # Criando tempo de renderização
    sleep(3)
    wait = WebDriverWait(driver, 3)

    # Localizar os elementos de resultados
    results_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc')))
    results_tittlets = [tittle.get_attribute('aria-label') for tittle in results_elements]

    # Aguardar os elementos serem clickaveis
    element = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'hfpxzc')))

    # Clickar no elemento
    element.click()

    # Esperar até que os elementos de informação estejam presentes
    wait = WebDriverWait(driver, timeout=3)
    info_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'Io6YTe')))

    # Armazenar informações na variavel
    info_texts = [element.text for element in info_elements]

    # Voltar para a página anterior
    driver.back()

    # Esperar até que os elementos de resultados estejam presentes novamente
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'hfpxzc')))

    # Incluir as devidas informações nos seus campos
    name.append(results_tittlets[0])
    address.append(info_texts[0])
    comments.append(info_texts[1])
    for info in info_texts:
        if '(' in info:
            number.append(info)

    # Criar um DataFrame a partir do dicionário
    return_dataframe = pd.DataFrame({
        'Nome': name,
        'Endereço': address,
        'Telefone': number,
        'Informações Adicionais': comments,
        })

    return_dataframe['Selecionar'] = return_dataframe.apply(lambda _: '<input type="checkbox">', axis=1)

    # Convertendo DataFrame para HTML
    result_html = return_dataframe.to_html(index=False, escape=False)

    # Encerrar o driver
    driver.quit()

    return render(request, 'return_page.html', {'result_html': result_html})

def teste_input(request):
    global teste
    if request.method == 'POST':
        input = request.POST.get('message')
        teste = f"O nome enviado foi: {input}"
        print(teste)
    return render(request, ' return_page.html', {'teste':teste})

