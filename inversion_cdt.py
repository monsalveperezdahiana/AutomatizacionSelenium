from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)


try:
    driver.get("https://cdt.credifamilia.com/")
    driver.maximize_window()


    # Esperar a que cargue el DOM principal
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


    # Click en el enlace real "SIMULADOR CDT"
    simulador_link = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[@href='#simularCDT' and normalize-space()='SIMULADOR CDT']")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", simulador_link)
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='#simularCDT' and normalize-space()='SIMULADOR CDT']")
        )
    )
    driver.execute_script("arguments[0].click();", simulador_link)


    # Esperar que procese la respuesta ingresada
    inversion_input = wait.until(
        EC.visibility_of_element_located((By.ID, "simuladorForm:inversion_input"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", inversion_input)
    time.sleep(1)


    # 3) Limpiar y escribir el valor
    inversion_input.click()
    inversion_input.send_keys(Keys.CONTROL, "a")
    inversion_input.send_keys(Keys.DELETE)
    inversion_input.send_keys("50000000")
    inversion_input.send_keys(Keys.TAB)


    # Esperar a que PrimeFaces actualice el hidden input
    wait.until(
        lambda d: d.find_element(By.ID, "simuladorForm:inversion_hinput").get_attribute("value") not in ("", "0", "0.0")
    )


    # Resultado
    resultado = wait.until(
        EC.presence_of_element_located((By.ID, "simuladorForm:resultado"))
    )
    texto_antes = resultado.text


    # 6) Ejecutar la función JS real del simulador
    driver.execute_script("simular();")


    # Resultados
    wait.until(
        lambda d: d.find_element(By.ID, "simuladorForm:resultado").text != texto_antes
    )


    print("Simulación ejecutada correctamente")
    print(driver.find_element(By.ID, "simuladorForm:resultado").text)


   
    time.sleep(5)


finally:
    driver.quit()
