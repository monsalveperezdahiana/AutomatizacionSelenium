import unittest
import time


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException




class PruebaRegistroCDT(unittest.TestCase):


    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 25)


    def esperar_ajax(self, timeout=15):
        """
        Espera a que terminen las peticiones AJAX de jQuery/PrimeFaces.
        """
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script(
                    "return (window.jQuery ? jQuery.active === 0 : true);"
                )
            )
        except TimeoutException:
            pass
        time.sleep(0.4)


    def scroll_al_elemento(self, by, locator):
        elem = self.wait.until(EC.presence_of_element_located((by, locator)))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", elem
        )
        return elem


    def escribir_input_texto(self, field_id, texto):
        """
        Para input text normales de PrimeFaces.
        """
        campo = self.wait.until(EC.element_to_be_clickable((By.ID, field_id)))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", campo
        )


        campo.click()
        campo.send_keys(Keys.CONTROL, "a")
        campo.send_keys(Keys.DELETE)
        campo.send_keys(texto)


        # Disparar blur/change para que PrimeFaces procese el valor
        campo.send_keys(Keys.TAB)
        self.esperar_ajax()


    def escribir_input_number(self, input_id, hinput_id, valor):
        """
        Para InputNumber de PrimeFaces.
        Escribe en el visible y valida que el hidden quede poblado.
        """
        campo = self.wait.until(EC.element_to_be_clickable((By.ID, input_id)))
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", campo
        )


        campo.click()
        campo.send_keys(Keys.CONTROL, "a")
        campo.send_keys(Keys.DELETE)
        campo.send_keys(str(valor))


        # Forzar eventos
        self.driver.execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('blur', { bubbles: true }));
        """, campo)


        campo.send_keys(Keys.TAB)
        self.esperar_ajax()


        # Validar que el hidden asociado tenga valor
        self.wait.until(
            lambda d: d.find_element(By.ID, hinput_id).get_attribute("value") not in ("", None)
        )


    def seleccionar_monto_por_valor(self, valor):
        """
        El combo de monto en PrimeFaces tiene un select hidden real:
        loginForm:montoCDT_input
        """
        select_id = "loginForm:montoCDT_input"


        self.wait.until(EC.presence_of_element_located((By.ID, select_id)))


        self.driver.execute_script("""
            const sel = arguments[0];
            const value = arguments[1];
            sel.value = value;
            sel.dispatchEvent(new Event('change', { bubbles: true }));
        """, self.driver.find_element(By.ID, select_id), valor)


        self.esperar_ajax()


        # Confirmar que sí quedó seleccionado
        self.wait.until(
            lambda d: d.find_element(By.ID, select_id).get_attribute("value") == valor
        )


    def marcar_autorizacion(self):
        """
        El checkbox real está oculto. Lo más estable es clicar la caja visible.
        """
        caja = self.wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#loginForm\\:autorizacion .ui-chkbox-box")
            )
        )


        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", caja
        )
        self.driver.execute_script("arguments[0].click();", caja)
        self.esperar_ajax()


        self.wait.until(
            lambda d: d.find_element(By.ID, "loginForm:autorizacion_input").is_selected()
        )


    def cerrar_popup_si_aparece(self):
        """
        A veces la página puede mostrar un popup al cargar.
        """
        try:
            cerrar = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.ID, "j_idt27"))
            )
            cerrar.click()
            self.esperar_ajax()
        except TimeoutException:
            pass


    def test_registro_cdt(self):
        driver = self.driver


        # Puedes entrar directo al ancla del formulario
        driver.get("https://cdt.credifamilia.com/#submitCDT")


        self.cerrar_popup_si_aparece()


        # Esperar el formulario principal
        self.wait.until(EC.presence_of_element_located((By.ID, "loginForm:nombreInp")))
        self.scroll_al_elemento(By.ID, "loginForm:nombreInp")


        # Datos de prueba
        nombres = "Dahiana"
        apellidos = "Monsalve Perez"
        cedula = "1234567890"
        correo = "monsalveperezdahiana@gmail.com"
        celular = "3001234567"
        referido = "1234"   # opcional, puedes dejarlo vacío
        monto_valor = "4000001"  # Entre $4.000.001 y $40.000.000


        # Llenado del formulario principal
        self.escribir_input_texto("loginForm:nombreInp", nombres)
        self.escribir_input_texto("loginForm:apellidos", apellidos)
        self.escribir_input_number("loginForm:cedula_input", "loginForm:cedula_hinput", cedula)
        self.escribir_input_texto("loginForm:correo", correo)
        self.escribir_input_number("loginForm:telefono_input", "loginForm:telefono_hinput", celular)


        # Campo opcional
        self.escribir_input_texto("loginForm:idReferido", referido)


        # Select monto
        self.seleccionar_monto_por_valor(monto_valor)


        # Checkbox términos
        self.marcar_autorizacion()


        # Opcional: enviar formulario
        boton = self.wait.until(
            EC.element_to_be_clickable((By.ID, "loginForm:submitButton"))
        )
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});", boton
        )


        # Si solo quieres validar que quedó lleno, comenta estas 2 líneas:
        self.driver.execute_script("arguments[0].click();", boton)
        self.esperar_ajax()


        # Pausa para inspección visual
        input("Presiona ENTER para cerrar el navegador...")


    def tearDown(self):
        self.driver.quit()




if __name__ == "__main__":
    unittest.main()
