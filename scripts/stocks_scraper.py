from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from multiprocessing import Pool

def cerrar_popup_cookies(driver):
    """Detecta y cierra la ventana emergente de cookies en Yahoo Finance"""
    try:
        boton_aceptar = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Aceptar todo')]"))
        )
        boton_aceptar.click()
        print(f"✅ Cookies aceptadas para {driver.current_url}.")
    except:
        print(f"⚠️ No apareció la ventana de cookies o ya fue cerrada para {driver.current_url}.")

def obtener_precio_accion(ticker):
    """Extrae el precio actual de una acción desde Yahoo Finance"""
    try:
        # Configurar Selenium con WebDriver Manager
        options = webdriver.ChromeOptions()
        options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        
        # Ejecutar en segundo plano (ocultar el navegador)
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

        # Inicializar WebDriver
        service = webdriver.chrome.service.Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        url = f"https://finance.yahoo.com/quote/{ticker}"
        driver.get(url)

        # Cerrar la ventana emergente de cookies
        cerrar_popup_cookies(driver)

        # Esperar hasta que el precio esté presente
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'container yf-16vvaki')]"))
        )

        # Obtener el precio
        precio_elemento = driver.find_element(By.XPATH, "//div[contains(@class, 'container yf-16vvaki')]")
        precio = precio_elemento.text

        driver.quit()
        return {"Ticker": ticker, "Precio": precio}
    
    except Exception as e:
        print(f"⚠️ Error obteniendo precio de {ticker}: {e}")
        driver.quit()
        return {"Ticker": ticker, "Precio": "No encontrado"}

def procesar_tickers(tickers, num_procesos=4):
    """Procesa los tickers usando múltiples procesos"""
    with Pool(processes=num_procesos) as pool:
        resultados = pool.map(obtener_precio_accion, tickers)
    return resultados

if __name__ == "__main__":
    tickers = ["AAPL", "GOOGL", "TSLA", "AMZN"]  # Lista de acciones a consultar
    
    # Procesar los tickers en paralelo
    datos = procesar_tickers(tickers, num_procesos=4)

    # Mostrar resultados individualmente
    for dato in datos:
        print(f"📢 {dato['Ticker']}: ${dato['Precio']}")

    # Crear DataFrame con Pandas y mostrarlo
    df = pd.DataFrame(datos)
    print("\n📊 **Tabla de Precios de Acciones**")
    print(df)