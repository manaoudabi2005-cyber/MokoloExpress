from flask import Flask, render_template, request, jsonify, session
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os
from threading import Lock

app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_paiement'

# Verrou pour éviter les conflits Selenium
selenium_lock = Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/paiement', methods=['POST'])
def api_paiement():
    data = request.json
    mode = data.get('mode')  # 'orange_money' ou 'mobile_money'
    numero = data.get('numero')
    
    if not mode or not numero:
        return jsonify({'error': 'Mode et numéro requis'}), 400
    
    # Lancer Selenium en arrière-plan
    try:
        with selenium_lock:
            result = executer_automatisation(mode, numero)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def executer_automatisation(mode_paiement, numero):
    """Automatisation Selenium complète"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Invisible
    chrome_options.add_argument("--no-sandbox")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Recharger la page via Flask (localhost)
        driver.get('http://127.0.0.1:5000')
        
        wait = WebDriverWait(driver, 10)
        
        # 1. Sélectionner mode paiement
        if mode_paiement == 'orange_money':
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Orange Money')]")))
        else:
            btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Mobile Money')]")))
        btn.click()
        
        # 2. Saisir numéro
        input_num = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Numéro de téléphone']")))
        input_num.clear()
        input_num.send_keys(numero)
        
        # 3. Valider numéro
        valider_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Valider')]")
        valider_btn.click()
        
        # 4. Attendre paiement manuel (status simulé)
        time.sleep(3)  # Simulation SMS envoyé
        
        return {
            'status': 'paiement_attendu',
            'message': f'Code envoyé à {numero}. Effectuez le paiement Orange Money puis cliquez "Valider" sur la page.'
        }
        
    finally:
        driver.quit()

@app.route('/api/valider-paiement', methods=['POST'])
def valider_paiement():
    """API pour valider après paiement téléphone"""
    numero = request.json.get('numero')
    
    # Simuler vérification paiement (Orange Money API réelle ici)
    if verifie_paiement(numero):
        session['paye'] = True
        return jsonify({'status': 'success', 'redirect': '/pages-suivantes'})
    return jsonify({'error': 'Paiement non détecté'}), 400

def verifie_paiement(numero):
    """Simulation - Remplacez par vraie API Orange Money"""
    return True  # Pour démo

@app.route('/pages-suivantes')
def pages_suivantes():
    if session.get('paye'):
        return "<h1>🎉 Accès autorisé ! Pages suivantes</h1>"
    return "❌ Paiement requis", 403

if __name__ == '__main__':
    app.run(debug=True, port=5000)
