import time  # Arquivando Valores das Variaáveis


def result_table(name, address, number, comments):
    result_dic = {
        "Resultado": name,
        "Endereço": address,
        "Telefone": number,
        "Observações": comments,
    }
    return result_dic


# Imports para o Projeto
from django.shortcuts import render
from django.http import HttpResponse
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

# Rendenizando página HomePage
selected_phones = []


def homepage(request):
    return render(request, 'homepage.html')


# Rendenizando página Search_Page
def search(request):
    return render(request, 'search_page.html')


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

    url = 'https://www.google.com.br/maps/search/{}+{}/@-24.0416944,-46.5883118,12z/data=!3m1!4b1?entry=ttu'.format(
        new_local, new_county)

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

    # Crie uma lista para armazenar o estado do checkbox para cada linha
    for num in number:
        number_more_country = '+55 ' + num
        new_number = number_more_country.replace('(', '').replace(')', '')
        checkbox_states = (
            '<div style="display: flex; justify-content: center; transform: scale(1.5);">'
            f'<input type="checkbox" name="Selecionar" value="{new_number}">'
            '</div>'
        )

    # Criar um DataFrame a partir do dicionário
    return_dataframe = pd.DataFrame({
        'Nome': name,
        'Endereço': address,
        'Telefone': number,
        'Informações Adicionais': comments,
        'Selecionar': checkbox_states
    })

    return_dataframe['Telefone'] = return_dataframe['Telefone'].astype(str)

    # Convertendo DataFrame para HTML
    result_html = return_dataframe.to_html(index=False, escape=False)

    # Encerrar o driver
    driver.quit()

    contact = number[0]
    global new_contact
    new_contact = '+55 ' + contact.replace('(', '').replace(')', '')

    return render(request, 'return_page.html', {'result_html': result_html})

    # Automatizando o WhatsApp!
def auto_whatsapp(request):
    global new_contact  # Declarando a variável contact como global

    # Configuração Driver.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Adicionando valores as variáveis.
    url_whatsapp = 'https://web.whatsapp.com/'

    # Se o método da requisição for POST, a variável contact foi definida anteriormente em all_results
    if request.method == 'POST':
        message = request.POST.get('message')

        # Abrindo o site utilizando a variável.
        driver.get(url_whatsapp)

        # Aguardando a página abrir e o usuário adicionar o whatsapp.
        wait = WebDriverWait(driver, timeout=120)

        # Buscando a opção de nova conversa
        new_conversation = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Nova conversa"]')))
        new_conversation.click()

        # Adicionando uma espera global para evitar fechamento do site.
        driver.implicitly_wait(2)

        # Localizando a barra de Pesquisa e apagando ela.
        search_bar = driver.find_element(By.XPATH, '//div[@title="Caixa de texto de pesquisa"]')
        search_bar.send_keys(new_contact)
        search_bar.send_keys(Keys.CONTROL + 'a')
        search_bar.send_keys(Keys.DELETE)
        search_bar.send_keys(new_contact)

        # Localizando o contato e entrando na conversa, adicionando um tempo de espera.
        contact_search = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@title="{}"]'.format(new_contact))))
        time.sleep(10)
        contact_search.click()
        wait = WebDriverWait(driver, timeout=10)

        # Clickando na barra de mensagem e formatando para enviar a mensagem.
        message_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Digite uma mensagem"]')))
        message_bar.send_keys(Keys.CONTROL + 'a')
        message_bar.send_keys(Keys.DELETE)
        message_bar.send_keys(message)
        message_bar.send_keys(Keys.RETURN)

        try:
            enviar = driver.find_element(By.XPATH, '//button[@aria-label="Enviar"]')
            wait = WebDriverWait(driver, timeout=3)
            enviar.click()

        except NoSuchElementException:
            pass

        # Saindo do site após realizar o envio da mensagem solicitada.
        driver.quit()

        return render(request, 'auto_whatsapp_page')
    else:
        return HttpResponse("Método não suportado")
