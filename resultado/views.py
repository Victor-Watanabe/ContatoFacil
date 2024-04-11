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
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException


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
    global formatted_contact
    formatted_contact = new_contact.replace('9'[0],'',1)

    return render(request, 'return_page.html', {'result_html': result_html})

    # Automatizando o WhatsApp!
def auto_whatsapp(request):
    # Declarando a variável contact como global
    global new_contact
    global formatted_contact

    # Configuração Driver.
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Adicionando valores as variáveis.
    url_whatsapp = "https://web.whatsapp.com/"

    # Se o método da requisição for POST, a variável contact foi definida anteriormente em all_results
    if request.method == 'POST':
        message = request.POST.get('message')

        # Aguardando a página abrir e o usuário adicionar o whatsapp.
        wait = WebDriverWait(driver, timeout=10)

        # Abrindo o site utilizando a variável.
        driver.get(url_whatsapp)

        wait = WebDriverWait(driver, timeout=60)

        try:
            # Se a conversa não existir, clique em "Nova conversa"
            new_conversation = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Nova conversa"]')))
            new_conversation.click()

            # Aguarde até que a barra de pesquisa esteja disponível
            search_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Caixa de texto de pesquisa"]')))
            search_bar.click()
            sleep(3)

        except TimeoutException:
            return render(request, 'timeout_error.html')

        try:
            # Localize a barra de Pesquisa e apague o conteúdo anterior.
            wait = WebDriverWait(driver, timeout=45)
            search_bar.send_keys(new_contact)
            search_bar.send_keys(Keys.CONTROL + 'a')
            search_bar.send_keys(Keys.DELETE)
            search_bar.send_keys(new_contact)

            # Localize o contato e clique nele
            wait = WebDriverWait(driver, timeout=45)
            contact_search = wait.until(EC.presence_of_element_located((By.XPATH,'//span[@title="{}"]'.format(new_contact))))
            sleep(3)
            contact_search.click()

        except (TimeoutException, ElementClickInterceptedException):
            try:
                # Caso o contato não tenha o número '9' no início dele, vai ser realizado um tratamento de dados para a correção do erro
                wait = WebDriverWait(driver, timeout=15)
                contact_search = wait.until(EC.presence_of_element_located((By.XPATH,'//span[@title="{}"]'.format(formatted_contact))))
                sleep(3)
                contact_search.click()

            except (TimeoutException, ElementClickInterceptedException):
                try:
                    # Voltando a página inicial de conversas do WhatsApp
                    back = driver.find_element(By.XPATH, '//div[@aria-label="Voltar"]')
                    back.click()
                    sleep(3)

                    # Aguardando o site renderizar a caixa de texto de pesquisa e utilizando ela para consulta de conversas já existentes
                    search_bar_2 = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Caixa de texto de pesquisa"]')))
                    search_bar_2.click()
                    sleep(3)

                    # Pesquisando o contato na barra de pesquisas
                    search_bar_2.send_keys(new_contact)
                    search_bar_2.send_keys(Keys.CONTROL + 'a')
                    search_bar_2.send_keys(Keys.DELETE)
                    search_bar_2.send_keys(new_contact)
                    sleep(3)

                    try:
                        # Procurando o resultado da pesquisa
                        wait = WebDriverWait(driver, timeout=10)
                        contact_search = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@title="{}"]'.format(new_contact))))
                        contact_search.click()

                    except (TimeoutException, ElementClickInterceptedException):
                        try:
                            wait = WebDriverWait(driver, timeout=10)
                            contact_search = wait.until(EC.presence_of_element_located((By.XPATH, '//span[@title="{}"]'.format(formatted_contact))))
                            contact_search.click()

                        except (TimeoutException, ElementClickInterceptedException):
                            return render(request, 'others_errors.html')

                    # Anexando a mensagem do HTML anterior
                    wait = WebDriverWait(driver, timeout=30)
                    message_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Digite uma mensagem"]')))
                    message_bar.send_keys(Keys.CONTROL + 'a')
                    message_bar.send_keys(Keys.DELETE)
                    message_bar.send_keys(message)
                    message_bar.send_keys(Keys.RETURN)

                    try:
                        # Tentando realizar o envio através do botão "Enviar"
                        enviar = driver.find_element(By.XPATH, '//button[@aria-label="Enviar"]')
                        wait = WebDriverWait(driver, timeout=3)
                        enviar.click()

                    except NoSuchElementException:
                        return render(request, 'others_errors.html')

                except NoSuchElementException:
                    return render(request, 'others_errors.html')

        # Adicione um tempo de espera para garantir que a conversa foi aberta
        wait = WebDriverWait(driver, timeout=60)

        # Clique na barra de mensagem e envie a mensagem
        message_bar = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@title="Digite uma mensagem"]')))
        message_bar.send_keys(Keys.CONTROL + 'a')
        message_bar.send_keys(Keys.DELETE)
        message_bar.send_keys(message)
        message_bar.send_keys(Keys.RETURN)

        # Tente encontrar o botão "Enviar" e clique nele
        try:
            enviar = driver.find_element(By.XPATH, '//button[@aria-label="Enviar"]')
            wait = WebDriverWait(driver, timeout=3)
            enviar.click()

        except NoSuchElementException:
            pass

        sleep(3)

        return render(request, 'auto_whatsapp_page.html')

    # Voltar até o local de pesquisa de conversas já realizadas.
    else:
        return render(request, 'others_errors.html')