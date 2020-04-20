import sys
import re
import argparse
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
import multiprocessing
sys.path.append("./sources/") if "./sources/" not in sys.path else ''
import utils

# Entenda os números de CRM:
# Número seguido da letra ‘P’: inscrição provisória realizada em atendimento a liminar.
# Número precedido da sigla ‘EME’: inscrição de estudante médico estrangeiro.
# Número precedido do número ‘300’: inscrição de médico estrangeiro com visto provisório.

def save_dataframe(df, filepath, append = True):
    if append and utils.check_file(filepath):   
        print ("Appending to existing dataframe")
        df_saved = pd.read_csv(filepath, sep=';')
        df = pd.concat([df_saved, df])

    df.to_csv(filepath, sep=';', index=None)
    print ("File saved at {}".format(filepath))

def scrap_state(uf, start_page = 1, end_page = -1, append = True):
    """ Extracts all physicians' profiles from a given state (uf).
        If start_page > 1, a file containing previous scrap for that 
        state is loaded.
    
    Arguments:
        uf {string} -- state abbreviation
    
    Keyword Arguments:
        start_page {int} -- which page to start the scrapping (default: {1})
        start_page {int} -- which page to end the scrapping (default: {-1})
    
    Returns:
        boolean -- whether or not the scrap was successfull
    """    
    
    print ("Scrapping ", uf)
    
    options = webdriver.chrome.options.Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    try:
        # Setting driver and variables
        progbar = utils.ProgressBar(elapsed_time=True)        

        url = "https://portal.cfm.org.br/index.php?option=com_medicos&nomeMedico=&ufMedico={}&crmMedico=&municipioMedico=&tipoInscricaoMedico=&situacaoMedico=&detalheSituacaoMedico=&especialidadeMedico=&areaAtuacaoMedico=&pagina=3"
        url = url.format(uf)
        driver.get(url)

        # Searching for the total number of pages to scrap
        result = re.search("Mostrando página \d de (\d+)", driver.page_source)
        if result is not None:
            print ("Total number of pages to scrap: ", result.groups()[0])

        if end_page == -1:            
            end_page = 15000 if result == None else int(result.groups()[0])            

        print ("Scrapping from pages {} to {} at {}".format(
                  start_page, end_page, uf))
        
        # If start_page > 1, check an existing file with previous scrap
        
        df = pd.DataFrame(columns=["page", "name", "crm", "state", 
            "subscription_date", "subscription_type", "status", 
            "second_subscription", "address", "phone", "photo_url"])
        
        progbar.update_progress(0)
        for page in range(start_page, end_page, 1):
            progbar.update_progress((page-1)/end_page)
        
            # Checking if any profiles are being shown
            if (len(driver.find_elements_by_class_name("resultado-mobile-coluna")) == 0):
                input("No profiles found for page {}. Reenter the captcha:".format(page))
            
            perfis = driver.find_elements_by_class_name("resultado-mobile-coluna")
            photos = driver.find_elements_by_class_name("img-thumbnail")
            
            # Extracting information from each profile
            for i_profile, profile in enumerate(perfis):    
                dados = profile.text.split('\n')

                name = dados[0]

                result = re.search("\d+", dados[1])
                crm = None if not result else result.group()

                result = re.search("\w{2}$", dados[1])
                state = None if not result else result.group()

                result = re.search("Data de Inscrição: (.*)", dados[2])
                subscription_date = None if result == None else result.groups()[0]

                result = re.search("Inscrição: (.*)", dados[3])
                subscription_type = None if result == None else result.groups()[0]

                result = re.search("Situação: (.*)", dados[4])
                status = None if result == None else result.groups()[0]

                result = re.search("Inscrições em outro estado: (.*)", dados[5])
                second_subscription = None if result == None else result.groups()[0]
                
                result = re.search("Especialidades/Áreas de Atuação: (.*)", dados[6])
                specialty = None if result == None else result.groups()[0]

                result = re.search("Endereço: (.*)", dados[7])
                address = None if result == 0 else result.groups()[0]

                result = re.search("Telefone\(s\): (.*)", dados[8])
                phone = None if result == None else result.groups()[0]

                photo_url = photos[i_profile].get_attribute("src")
                
                df.loc[df.shape[0]] = [page, name, crm, state, subscription_date, 
                    subscription_type, status, second_subscription, address, 
                    phone, photo_url]

            # Accessing next page of profiles
            next_url = re.sub(r"&pagina=\d+", "&pagina={}".format(page+1), url)
            driver.get(next_url)
        
        print ("Number of extracted profiles for {}: {}".format(uf, df.shape[0]))

        filepath = "./data/profiles/df_{}.csv".format(uf)

        save_dataframe(df, filepath, append)

        driver.close()

        return True

    except Exception as e:
        print ("Error scrapping {} at page {}: {}".format(uf, page, e))

    save_dataframe(df, filepath, append)

    driver.close()

    return False

if __name__ == "__main__":
       
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--start_page', '-s', dest='start_page', default=1, help='Index of the first page to start scrapping')
    parser.add_argument('--end_page', '-e', dest='end_page', default=-1, help='Index of the last page to scrap')
    parser.add_argument('--uf', '-u', dest='uf', default=None, help='State to run the script')
    parser.add_argument('--append', '-a', dest='append', default=1, help='Whether or not to append process to existing dataframe')
    args = parser.parse_args()

    uf = args.uf
    start_page = int(args.start_page)
    end_page = int(args.end_page)
    append = bool(int(args.append))

    if uf is not None:
        scrap_state(uf, start_page, end_page, append)
    else:

        ufs = [
            # 'AC', # OK
            # 'AL', # OK
            # 'AM', # OK
            # 'AP', # OK
            # 'BA', # OK
            # 'CE', # OK
            # 'DF', # OK
            # 'ES', # OK
            # 'GO', # OK
            # 'MA', # OK
            # 'MG', # OK
            # 'MT', # OK
            # 'MS', # OK
            # 'PA', # OK
            # 'PB', # OK
            # 'PE', # OK
            # 'PI', # OK
            # 'PR', # OK
            # 'RN', # OK
            # 'SC', # OK
            # 'RJ', # Progress
            # 'RS', # OK
            # 'RO', # OK
            # 'RR', # OK
            # 'BR', 
            # 'SP',
            # 'SE', # OK
            # 'TO', # OK
        ]

        processes = list()

        for uf in ufs:        
            dict_parameters = dict()
            dict_parameters[uf] = uf
            p = multiprocessing.Process(target=scrap_state, args=(dict_parameters))
            processes.append(p)
            p.start()

        for process in processes:
            process.join()
