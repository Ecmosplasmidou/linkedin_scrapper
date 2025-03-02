from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os
import time
import random
import sys

sys.stdout.reconfigure(encoding='utf-8')


gecko_driver_path = r"C:\Users\cassa\Desktop\scrapper_linkedin\geckodriver.exe"
firefox_binary_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"


options = Options()
options.binary_location = firefox_binary_path  
options.add_argument("--width=1280")  
options.add_argument("--height=800") 
options.set_preference("dom.webdriver.enabled", False)  


service = Service(gecko_driver_path)
driver = webdriver.Firefox(service=service, options=options)



def login_linkedin(email, password):
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password + Keys.RETURN)
    time.sleep(5)




def search_linkedin(ville):
    search_url = f"https://www.linkedin.com/search/results/people/?keywords=RH%20recruteur%20{ville}"
    driver.get(search_url)

    profils = []

    for page in range(1, 4):  
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//li[contains(@class, 'ypvdbbHqnyMugzFsPQMcnlxliOdDzJqbvXk')]"))
            )
        except Exception as e:
            print(f"❌ Aucun résultat trouvé pour {ville} à la page {page} : {e}")
            break


        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(3, 6))


        results = driver.find_elements(By.XPATH, "//li[contains(@class, 'ypvdbbHqnyMugzFsPQMcnlxliOdDzJqbvXk')]")

        for result in results:
            try:
                try:
                    profil_url = result.find_element(By.XPATH, ".//a[contains(@href, '/in/')]").get_attribute("href")
                except:
                    profil_url = None 

                try:
                    description = result.find_element(By.XPATH, ".//div[contains(@class, 't-black t-normal')]").text.lower()
                except:
                    description = ""


                try:
                    location = result.find_element(By.XPATH, ".//div[contains(@class, 't-14 t-normal')]").text.lower()
                except:
                    location = ""

                if profil_url and ("rh" in description or "ressources humaines" in description or "chargé de recrutement" in description and "it" in description) and any(v in location for v in ["toulouse", "colomiers", "blagnac"]):
                    profils.append(profil_url)
                    print(f"✅ Profil trouvé : {profil_url} - {description} - {location}")

            except Exception as e:
                print(f"❌ Erreur lors de l'analyse d'un résultat : {e}")


        try:
            next_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Suivant')]")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(random.uniform(3, 6))
        except Exception as e:
            print(f"❌ Impossible de trouver le bouton 'Suivant' à la page {page} : {e}")
            break

    print(f"🔍 {len(profils)} profils trouvés pour {ville}")


    with open("page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    return profils


def send_message(profil_url, message):
    print(f"📌 Accès au profil : {profil_url}")
    driver.get(profil_url)
    time.sleep(5) 
    
    if "checkpoint/challenge" in driver.current_url:
        print("❌ LinkedIn a détecté un bot, résolution manuelle nécessaire.")
        driver.quit()
        exit()
        
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[span[text()='Message']]"))
        )
        message_button = driver.find_element(By.XPATH, "//button[span[text()='Message']]")
        driver.execute_script("arguments[0].click();", message_button)
        time.sleep(2)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@contenteditable='true']"))
        )
        message_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
        message_box.send_keys(message)
        message_box.send_keys(Keys.RETURN)
        
        send_button = driver.find_element(By.XPATH, "//button[contains(@class, 'msg-form__send-button')]")
        driver.execute_script("arguments[0].click();", send_button)
        print(f"✅ Message envoyé à {profil_url}")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'envoi du message à {profil_url} : {e}")
    
load_dotenv()
    
email = os.getenv('email')
password = os.getenv('password')

login_linkedin(email, password)

villes = ["toulouse", "colomiers", "blagnac"]
tous_profils = []

for ville in villes:
    profils = search_linkedin(ville)
    tous_profils.extend(profils)    
    
print(f"{len(tous_profils)} profils trouvés")   

message = f"""Bonjour,

Je me permets de vous contacter car je suis actuellement à la recherche d’une opportunité en CDI en tant que développeur Python ou une alternance en tant que Data Scientist.

Je prépare actuellement un Master Expert en Systèmes d’Informations à la 3W Academy, et je suis passionné par l’analyse de données, le machine learning et le développement en Python. Je serais ravi d’échanger avec vous sur d’éventuelles opportunités dans votre entreprise.

Seriez-vous disponible pour en discuter ?  

Merci d’avance pour votre retour.

Cordialement,

MAHADAWOO Cassam"""

for profil in tous_profils:
    send_message(profil, message)
    time.sleep(7)
    
driver.quit()
print("Fin de la session")