from io import BytesIO
from PIL import Image
import os.path
from datetime import datetime
import time
from typing import Optional
from selenium.webdriver.common.alert import Alert
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.select import Select
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService  # ChromeService que se utiliza para iniciar el servicio de Chrome.
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver

class BasePage(By):
    
    VALID_BROWSERS = {'chrome', 'firefox', 'edge'}
    # Constructor
    def __init__(self, 
                 driver: Optional[WebDriver] = None,
                 driver_to_use: str = 'chrome', 
                 wait: int = 10, 
                 highlight: bool = False, 
                 proxy: str = '', 
                 load_timeout_site: int = 120, 
                 headless: bool = False, 
                 ignore_cert_errors: bool = True):
        
        driver_to_use = driver_to_use.lower()
        
        if driver_to_use not in self.VALID_BROWSERS:
            raise ValueError(f"Invalido 'driver_to_use': {driver_to_use}. solo se admite: {', '.join(self.VALID_BROWSERS)}.")
        
        if driver is None:
            if driver_to_use == 'firefox':
                firefox_options = webdriver.FirefoxOptions()
                if headless:
                    firefox_options.add_argument("--headless")
                if proxy:
                    firefox_options.add_argument(f'--proxy-server={proxy}')
                if ignore_cert_errors:
                    firefox_options.set_preference("network.stricttransportsecurity.preloadlist", False)
                    firefox_options.set_preference("security.enterprise_roots.enabled", True)
                    firefox_options.set_preference("webdriver_accept_untrusted_certs", True)
                    firefox_options.set_preference("webdriver_assume_untrusted_issuer", False)
                self.driver = webdriver.Firefox(options=firefox_options, service=FirefoxService())
                
            elif driver_to_use == 'edge':
                edge_options = webdriver.EdgeOptions()
                edge_options.add_argument("--start-maximized")
                if headless:
                    edge_options.add_argument("--headless")
                if proxy:
                    edge_options.add_argument(f'--proxy-server={proxy}')
                if ignore_cert_errors:
                    edge_options.add_argument('--ignore-certificate-errors')
                self.driver = webdriver.Edge(options=edge_options, service=EdgeService())
                
            else:  # 'chrome' por defecto
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_experimental_option("detach", True)
                chrome_options.add_argument("disable-logging")
                chrome_options.add_argument('--allow-running-insecure-content')
                chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
                chrome_options.add_argument("--disable-extensions")
                if headless:
                    chrome_options.add_argument("--headless")
                if proxy:
                    chrome_options.add_argument(f'--proxy-server={proxy}')
                if ignore_cert_errors:
                    chrome_options.add_argument('--ignore-certificate-errors')
                self.driver = webdriver.Chrome(options=chrome_options, service=ChromeService())
                
        else:
            self.driver = driver
        
        self.driver.set_page_load_timeout(load_timeout_site)
        self.wait = WebDriverWait(self.driver, wait)
        self.actions = ActionChains(self.driver)
        self.highlight = highlight
        self.highlight_script = "arguments[0].style.border='10px ridge #d92356'"

    # Obtiene el driver actual.
    def get_driver_current(self):
        return self.driver
    
    # Obtiene el titulo de la página actual.
    def get_title(self):
        return self.driver.title

    # Abre el sitio web o archivo html.
    def navigate_to(self, url:str):
        try:
            self.driver.get(url)
  
        except WebDriverException as e:
            print(f"Error al navegar a la URL: {url}. más detalle: {e}")
            # traceback.print_exc()  # Imprime el rastro de la pila
            self.driver.quit()

    # Cierra el browser activo.
    def close_browser(self):
        self.driver.stop_client()
        # quit() method quits the driver instance, closing every associated window, which is opened.
        self.driver.close()
        self.driver.quit()

    # La funcion "find" devuelve un webElement en base al "locator" recibido.
    def find(self, locator: tuple) -> WebElement:
        try:
            # element = self.wait.until(ec.presence_of_element_located(locator))  # espera que esté presente
            element = self.wait.until(ec.visibility_of_element_located(locator))  # espera que esté visible
            # element = self.wait.until(ec.element_to_be_clickable(locator))  # espera que sea clickable
            if self.highlight:
                self.driver.execute_script(self.highlight_script, element)
            return element
        # except TimeoutException:
        except WebDriverException as e:
            print(f"Error al buscar webElement con el locator: {locator}. más detalle:  {e}")
            # traceback.print_exc()  # Imprime el rastro de la pila
            # Aquí manejas el caso cuando el elemento no es visible dentro del tiempo máximo de espera
            return None  # Otra opción es retornar None en caso de error

    # La funcion "limpia" un textbox.
    def clear_text(self, locator):
        element = self.find(locator)
        if element is not None:
            element.clear()

    # La funcion obtiene el texto de un textbox.
    def get_text(self, locator):
        element = self.find(locator)
        if element is not None:
            return element.text

    # La funcion inserta texto en un textbox.
    def set_text(self, locator, text_to_write):
        self.clear_text(locator)
        element = self.find(locator)
        if element is not None:
            element.send_keys(text_to_write)

    # La función click_element_js en tu código se utiliza para hacer clic en un
    # elemento web utilizando JavaScript. En lugar de utilizar el método click()
    def click_element_js(self, locator):
        element = self.find(locator)
        self.driver.execute_script("arguments[0].click();", element)

    # La función click_element en tu código se utiliza para hacer clic en un
    # elemento web identificado por un locator específico. 
    def click_element(self, locator):
        element = self.find(locator)
        if element is not None:
            element.click()
            if self.highlight:
                self.driver.execute_script(self.highlight_script, element)

    # Esta función devuelve la URL actual de la página
    # web que se está mostrando en el navegador.
    def current_url(self):
        return self.driver.current_url

    # La función maximize maximiza la ventana del navegador.
    def maximize(self):
        self.driver.maximize_window()

    # La función highlight_web_element en tu código utiliza JavaScript
    # para resaltar un elemento web en la página.
    def highlight_web_element(self, element):
        self.driver.execute_script(self.highlight_script, element)

    # La función sleep en tu código es una función estática que se utiliza para
    # pausar la ejecución de un script durante un número específico de segundos.
    @staticmethod
    def sleep(sec):
        time.sleep(sec)

    # La función switch_to_window en tu código permite cambiar el enfoque a una
    # ventana específica en una aplicación web.
    def switch_to_window(self, window_number):
        # self.wait.until(ec.number_of_windows_to_be(2))
        self.sleep(2)
        try:
            self.driver.switch_to.window(self.driver.window_handles[window_number])
        except IndexError as err:
            print(f'\n\n##############\nNo existe la ventana "{window_number}":', err, '\n##############\n')
        except Exception as err:
            print('\n\n##############\nSalió por error general:', err, '\n##############\n')

    # La función scroll_down en tu código permite desplazar la página hacia abajo
    # en la cantidad de píxeles especificados.
    def scroll_down(self, pixels):
        # self.execute_js_script(f"window.scrollBy(0,{pixels})")
        js_script = f"window.scrollBy(0,{pixels})"
        return self.driver.execute_script(js_script)


    # La función scroll_to_element se utiliza para desplazar la página web de
    # modo que un elemento específico identificado 
    # por un locator quede visible en la ventana del navegador.
    def scroll_to_element(self, locator):
        element = self.find(locator)
        self.actions.move_to_element(element).perform()
        # self.driver.execute_script("arguments[0].scrollIntoView();", element)

    # La función double_click se utiliza para realizar un doble clic sobre un
    # elemento web identificado por un locator específico.
    def double_click(self, locator):
        element = self.find(locator)
        self.actions.double_click(element).perform()

    # La función right_click se utiliza para realizar un clic derecho en un
    # elemento web identificado por un locator específico.
    def right_click(self, locator):
        element = self.find(locator)
        self.actions.context_click(element).perform()

    # La función take_screenshot se utiliza para capturar una captura de pantalla de la página web actual en el
    # navegador y guardarla en un archivo con un título específico.
    def take_screenshot(self, title: str) -> str:
        self.sleep(3)
        date = datetime.now().strftime('%Y%m%d_%H%M%S')
        if not os.path.exists(os.path.join(os.getcwd(), 'screenshots')):
            os.mkdir('screenshots')
        save_path:str = 'screenshots/' + title + '_' + date + '.png'
        if self.driver.save_screenshot(save_path) == True:
             return save_path
        else:
             return None
    
    #  La funcion devuleve un array de bytes, es útil cuando se utiliza:
    #  from pytest_html_reporter import attach
    #  from PIL import Image
    #  img = Image.open('D:/MisProyectos/Selenium/test/imagen.png')
    #  attach(get_screenshot_from_file(img))
    def get_screenshot_from_file(self,img: Image) -> bytes:
        # Guarda la imagen en un objeto BytesIO en formato PNG
        with BytesIO() as buffer:
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_data = buffer.read()
        return img_data
        
    def get_screenshot_as_png(self) -> bytes:
        self.sleep(3)
        return self.driver.get_screenshot_as_png()
           
    # La función click_and_hold se utiliza para hacer clic y mantener presionado un
    # elemento web identificado por un localizador
    def click_and_hold(self, locator):
        element = self.wait.until(ec.element_to_be_clickable(locator))
        self.actions.click_and_hold(element).perform()

    # Libera la accion de un elemento. Esto podría ser útil, por ejemplo, en
    # una situación en la que necesitas arrastrar y soltar un elemento en una página web.
    def release(self, locator):
        element = self.wait.until(ec.element_to_be_clickable(locator))
        self.actions.release(element).perform()

    # la función está diseñada para ingresar un valor en una celda
    # editable de una tabla HTML
    # Ingresa un valor a una celda editable de una tabla html.
    def set_value_on_table(self, locator, row, column, text):
        if locator[0] == By.XPATH:
            locator = locator[0], locator[1] + f"/table/tbody/tr[{row}]/td[{column}]"
            self.set_text(locator, text)
        else:
            # Código a ejecutar si el locator no coincide con ningún caso anterior
            print("El locator debe ser: By.XPATH.")

    # La función get_value_from_table se utiliza para obtener el valor de una
    # celda en una tabla HTML.
    def get_value_from_table(self, locator, row, column):
        if locator[0] == By.XPATH:
            locator = locator[0], locator[1] + f"/table/tbody/tr[{row}]/td[{column}]"
            return self.get_text(locator)  # .set_text(locator, text)
        else:
            # Código a ejecutar si el locator no coincide con ningún caso anterior
            print("El locator no es By.XPATH.")

    # Esta función cambia el contexto actual al marco (frame) principal o
    # al marco "padre" si actualmente estás dentro de un marco. Es útil 
    # cuando has cambiado al contexto de un marco secundario y deseas volver 
    # al marco principal de la página web.
    def switch_to_parent_frame(self):
        self.driver.switch_to.parent_frame()

    # cambia el contexto al marco especificado en el argumento locator. Debes proporcionar un localizador
    # que identifique el marco al que deseas cambiar.
    def switch_to_frame(self, locator):
        iframe = self.find(locator)
        self.driver.switch_to.frame(iframe)

    # Se utiliza para actualizar la página actual en el navegador web.
    def refresh(self):
        self.driver.refresh()

    # se utiliza para aceptar (confirmar) una ventana emergente de alerta en una página web.
    def accept_alert(self):
        try:
            self.wait.until(ec.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.accept()
        except TimeoutException:
            print("no alert present")

    # Se utiliza para interactuar con una ventana emergente de alerta en una página web
    # si accept = True entonces se realiza el accept ademas de hacer el input.
    def accept_alert_with_text_input(self, text, accept=False):
        try:
            self.wait.until(ec.alert_is_present())
            alert = self.driver.switch_to.alert
            alert.send_keys(text)

            if accept:
                alert.accept()

        except TimeoutException:
            print("no alert present")

    # is_displayed se usa para verificar si el elemento es visible para el usuario o no:
    def is_displayed(self, locator) -> bool:
        element = self.find(locator)
        if element is not None:
            return element.is_displayed()
        else:
            return False

    # find puede devolver un WebElement o none (en caso que no se encuentre el webelement
    # por medio del locator)
    def is_enabled(self, locator):
        element = self.find(locator)
        if element is not None:
            return element.is_enabled()
        else:
            return None

    # se utiliza para verificar si un elemento de casilla de verificación (checkbox) está
    # marcado (seleccionado) o no.
    def is_checked(self, locator):
        element = self.find(locator)
        if element is not None:
            return element.is_selected()
        else:
            return None

    # devuelve la cantidad de items de un combo (select html)
    def get_dropdown_item_count(self, locator):
        select = Select(self.find(locator))
        return len(select.options)

    # devuelve los valores de un combo (select html)
    def get_all_dropdown_elements_list(self, locator):
        select = Select(self.find(locator))
        list_item = []
        for item in select.options:
            list_item.append(item)
        return list_item

    # devuelve los valores seleccionados de un combo (select multiple html)
    def get_dropdown_selected_item_list(self, locator):
        select = Select(self.find(locator))
        list_item = []
        for item in select.all_selected_options:
            list_item.append(item)
        return list_item

    # Selecciona el texto informado de una lista select x texto.
    def select_element_of_list_by_text(self, locator, text):
        select = Select(self.find(locator))
        select.select_by_visible_text(text)

    # Selecciona el texto informado de una lista select x index.
    def select_element_of_list_by_index(self, locator, index):
        select = Select(self.find(locator))
        select.select_by_index(index)

    # Valida la existencia de un valor dentro de un combo Select.
    def verify_item_in_dropdown(self, locator, text):
        select = Select(self.find(locator))
        for item in select.options:
            if text == item.text:
                return True
        return False

    # Tílda o marca una casilla del tipo checkbox.
    def select_checkbox(self, checkbox):
        self.find(checkbox).click()

    # Tílda o marca un radio button
    def select_radio_button(self, radio_button):
        self.find(radio_button).click()

    # solo funciona cuando no existe modal html
    def upload_file(self, locator, file_path):
        self.find(locator).send_keys(file_path)

    # se utiliza para eliminar todas las cookies del navegador
    def delete_all_cookies(self):
        self.driver.delete_all_cookies()

    # se utiliza para eliminar todas las cookies del navegador
    def get_cookies(self):
        self.driver.get_cookies()

    # Se utiliza para arrastrar y soltar un elemento web dentro de otro.
    def drag_and_drop(self, loc_source, loc_target):
        source_element = self.find(loc_source)
        target_element = self.find(loc_target)
        action_chains = ActionChains(self.driver)
        action_chains.drag_and_drop(source_element, target_element).perform()

    # Esto simulará el comportamiento del cursor del mouse cuando se desplaza sobre
    # el elemento en la página web.
    def hover_over_element(self, element):
        element_to_hover_over = self.find(element)
        action_chains = ActionChains(self.driver)
        action_chains.move_to_element(element_to_hover_over).perform()

    # esperar hasta que un elemento de la página web desaparezca de la vista, es decir, cuando
    # el elemento ya no sea visible en la página
    def wait_for_element_to_disappear(self, element):
        self.wait.until_not(ec.visibility_of_element_located(element))

    # se utiliza para esperar a que un elemento web sea clickable, es decir, que esté en
    # un estado en el que se le puede hacer clic.
    def wait_for_element_to_be_clickable(self, element):
        self.wait.until(ec.element_to_be_clickable(element))

    # se utiliza para obtener el valor de un atributo específico de un elemento web
    def get_attribute(self, element, attribute_name):
        element = self.find(element)
        return element.get_attribute(attribute_name)

    # Es útil cuando necesitas cambiar dinámicamente los atributos de un elemento en una página web.
    def set_attribute(self, element, attribute_name, attribute_value):
        element = self.find(element)
        script = f"arguments[0].setAttribute('{attribute_name}', '{attribute_value}');"
        self.driver.execute_script(script, element)

    # La función es útil para esperar situaciones en las que un elemento en la página cambia de
    # visibilidad,esperar hasta que un elemento web específico se vuelva invisible.
    def invisibility_of_element_located(self, locator):
        return self.wait.until(ec.invisibility_of_element_located(locator))

    # espera hasta que un elemento web especificado sea visible. Esto es útil cuando deseas
    # asegurarte de que un elemento se ha cargado y es 
    # visible en la página antes de realizar cualquier acción en él.
    def visibility_of_element_located(self, locator):
        return self.wait.until(ec.visibility_of_element_located(locator))
    
    #ejecuta script javascript (ej: "return window.localStorage.getItem('token')"")
    def execute_script(self, script:str):
        return self.driver.execute_script(script)
    
    # Devuelve el color de fondo del elemento web en formato hexadecimal.
    # Si el color no está configurado, devuelve 'none'.       
    def  get_color_of_element(self, locator) -> str:
        element:WebElement = self.find(locator)
        color:str = element.value_of_css_property('background-color')
        
        if color == 'rgba(0, 0, 0, 0)' or 'rgb(0, 0, 0)' or color == 'transparent':
            return 'none'
        
        if color.startswith('#'):
            return color
        
        return self.__rgb_to_hex(color)
    
    # Devuelve el color de fondo del elemento web en formato RGB.
    # Si el color no está configurado, devuelve 'none'.
    def get_color_of_element(self, locator) -> str:
        element: WebElement = self.find(locator)
        color: str = element.value_of_css_property('background-color')
        
        if color in ('rgba(0, 0, 0, 0)', 'rgb(0, 0, 0)', 'transparent'):
            return 'none'
        
        if color.startswith('#'):
            return color
        
        return self.__rgb_to_hex(color)

    # Devuelve altura, ancho, coordenadas X e X del elemento
    def get_size_coordinates(self, locator)->dict:
        
        elemente:WebElement = self.find(locator)
        elemente.rect
        
    # Devuelve el tamaño del elemento
    def get_size(self, locator)->dict:
        
        elemente:WebElement = self.find(locator)
        return elemente.size
    
    # Método privado
    def __rgb_to_hex(self, rgb: str) -> str:
    #Convierte un valor RGB en formato 'rgb(r, g, b)' o 'rgba(r, g, b, a)' a hexadecimal.
    # Elimina 'rgba(' o 'rgb(' y ')'
        rgb = rgb.replace('rgba(', '').replace('rgb(', '').replace(')', '')
        
        # Divide los valores
        values = list(map(int, rgb.split(', ')))
        
        # Si tiene 4 valores, es RGBA; si tiene 3, es RGB
        r, g, b = values[:3]  # Ignorar el canal alfa si es RGBA

        # Convertir a hexadecimal
        return f'#{r:02X}{g:02X}{b:02X}'