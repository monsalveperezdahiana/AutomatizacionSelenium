from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time


URL = "https://cdt.credifamilia.com/"


NOMBRES = "Dahiana"
APELLIDOS = "Monsalve"
CORREO = "correo@dominio.com"
CELULAR = "3001234567"


# Valores válidos del combo según el HTML:
# 100000     -> Entre $100.000 y $999.999
# 1000000    -> Entre $1.000.000 y $4.000.000
# 4000001    -> Entre $4.000.001 y $40.000.000
# 40000001   -> Entre $40.000.001 y 80.000.000
# 80000001   -> Más de $80.000.000
MONTO_VALOR = "4000001"


driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 25)




def esperar_ajax():
    """Espera a que terminen las peticiones AJAX/jQuery."""
    try:
        wait.until(
            lambda d: d.execute_script(
                "return (window.jQuery ? jQuery.active === 0 : true);"
            )
        )
    except Exception:
        pass
    time.sleep(0.4)




def esperar_formulario_wa():
    return wait.until(EC.presence_of_element_located((By.ID, "j_idt222")))




def cerrar_popup_si_aparece():
    try:
        btn = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.ID, "j_idt27"))
        )
        btn.click()
        esperar_ajax()
    except TimeoutException:
        pass




def abrir_panel_whatsapp():
    icono = wait.until(EC.element_to_be_clickable((By.ID, "j_idt493")))
    driver.execute_script("arguments[0].click();", icono)
    wait.until(EC.visibility_of_element_located((By.ID, "j_idt222:nombreInp")))
    esperar_ajax()




def limpiar_y_escribir(elem, texto):
    elem.click()
    elem.send_keys(Keys.CONTROL, "a")
    elem.send_keys(Keys.DELETE)
    elem.send_keys(texto)




def llenar_input_con_rerender(field_id, valor):
    """
    Para campos que actualizan todo el form j_idt222:
    nombre, apellidos, correo, autorización.
    """
    for intento in range(3):
        try:
            form_viejo = esperar_formulario_wa()


            campo = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", campo
            )
            limpiar_y_escribir(campo, valor)
            campo.send_keys(Keys.TAB)


            wait.until(EC.staleness_of(form_viejo))
            esperar_formulario_wa()
            esperar_ajax()
            return


        except StaleElementReferenceException:
            if intento == 2:
                raise
            time.sleep(1)




def llenar_input_simple(field_id, valor):
    """
    Para campos que no rehacen todo el form.
    """
    for intento in range(3):
        try:
            campo = wait.until(EC.element_to_be_clickable((By.ID, field_id)))
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", campo
            )
            limpiar_y_escribir(campo, valor)
            campo.send_keys(Keys.TAB)
            esperar_ajax()
            return


        except StaleElementReferenceException:
            if intento == 2:
                raise
            time.sleep(1)




def llenar_celular(valor):
    """
    El input visible es j_idt222:telefono_input y PrimeFaces mantiene además
    el hidden j_idt222:telefono_hinput.
    """
    llenar_input_simple("j_idt222:telefono_input", valor)


    wait.until(
        lambda d: d.find_element(By.ID, "j_idt222:telefono_hinput")
        .get_attribute("value")
        not in ("", None)
    )
    esperar_ajax()




def seleccionar_monto(valor_select):
    """
    Selecciona el combo hidden real y dispara change.
    """
    for intento in range(3):
        try:
            boton_viejo = wait.until(
                EC.presence_of_element_located((By.ID, "j_idt222:submitButton"))
            )


            select_real = wait.until(
                EC.presence_of_element_located((By.ID, "j_idt222:j_idt250_input"))
            )


            driver.execute_script(
                """
                const sel = arguments[0];
                const val = arguments[1];
                sel.value = val;
                sel.dispatchEvent(new Event('change', { bubbles: true }));
                """,
                select_real,
                valor_select,
            )


            # El monto actualiza el submitButton
            wait.until(EC.staleness_of(boton_viejo))


            wait.until(
                lambda d: d.find_element(By.ID, "j_idt222:j_idt250_input")
                .get_attribute("value")
                == valor_select
            )
            esperar_ajax()
            return


        except StaleElementReferenceException:
            if intento == 2:
                raise
            time.sleep(1)




def marcar_autorizacion():
    """
    El checkbox actualiza todo el form j_idt222.
    """
    for intento in range(3):
        try:
            form_viejo = esperar_formulario_wa()


            caja = wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#j_idt222\\:autorizacion .ui-chkbox-box")
                )
            )
            driver.execute_script("arguments[0].click();", caja)


            wait.until(EC.staleness_of(form_viejo))
            esperar_formulario_wa()


            wait.until(
                lambda d: d.find_element(By.ID, "j_idt222:autorizacion_input").is_selected()
            )
            esperar_ajax()
            return


        except StaleElementReferenceException:
            if intento == 2:
                raise
            time.sleep(1)




def esperar_boton_habilitado():
    wait.until(
        lambda d: (
            d.find_element(By.ID, "j_idt222:submitButton").get_attribute("disabled") is None
            and "ui-state-disabled"
            not in d.find_element(By.ID, "j_idt222:submitButton").get_attribute("class")
        )
    )




def click_chatear():
    ventanas_antes = driver.window_handles


    boton = wait.until(EC.element_to_be_clickable((By.ID, "j_idt222:submitButton")))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", boton)
    driver.execute_script("arguments[0].click();", boton)


    # El form tiene target="_blank", así que debería abrir nueva pestaña/ventana
    wait.until(lambda d: len(d.window_handles) > len(ventanas_antes))


    nueva = [w for w in driver.window_handles if w not in ventanas_antes][0]
    driver.switch_to.window(nueva)


    wait.until(
        lambda d: (
            "whatsapp" in d.current_url.lower()
            or "wa.me" in d.current_url.lower()
            or "api.whatsapp.com" in d.current_url.lower()
            or "web.whatsapp.com" in d.current_url.lower()
        )
    )




try:
    driver.get(URL)
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))


    cerrar_popup_si_aparece()
    abrir_panel_whatsapp()


    # Estos rehacen el form completo
    llenar_input_con_rerender("j_idt222:nombreInp", NOMBRES)
    llenar_input_con_rerender("j_idt222:apellidos", APELLIDOS)
    llenar_input_con_rerender("j_idt222:correo", CORREO)


    # Este actualiza el botón, no todo el form
    llenar_celular(CELULAR)


    # Este actualiza el botón
    seleccionar_monto(MONTO_VALOR)


    # Este rehace el form completo
    marcar_autorizacion()


    esperar_boton_habilitado()
    click_chatear()


    print("Flujo completado correctamente")
    print("URL final:", driver.current_url)
    time.sleep(5)


except Exception as e:
    driver.save_screenshot("error_chat_whatsapp.png")
    print("Error en la automatización:", e)


finally:
    driver.quit()
