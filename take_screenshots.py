"""Auto-capture real screenshots of the College Leave Portal demo."""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time, os
BASE_URL = "http://127.0.0.1:8000"
OUT_DIR = "screenshots"
os.makedirs(OUT_DIR, exist_ok=True)
driver = webdriver.Chrome()
driver.set_window_size(1280, 900)
def wait(seconds=0.5):
    time.sleep(seconds)
def shot(name):
    path = os.path.join(OUT_DIR, name)
    driver.save_screenshot(path)
    print(f"[SAVED] {path}")
def reset_app():
    driver.get(BASE_URL + "/index.html")
    driver.execute_script("localStorage.clear();")
    driver.refresh()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "loginSection")))
def login(username, password):
    driver.find_element(By.ID, "username").clear()
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "loginBtn").click()
def fill_leave(start, end, reason):
    driver.execute_script(
        "document.getElementById('startDate').value = arguments[0];"
        "document.getElementById('endDate').value = arguments[1];"
        "document.getElementById('reason').value = arguments[2];",
        start, end, reason)
print("\n=== Experiment 7 (desktop) ===")
reset_app()
login("student1", "pass123")
WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.ID, "studentDashboard")))
wait()
shot("exp7_01_login_ok.png")
driver.find_element(By.ID, "logoutBtn").click()
wait()
login("student1", "wrong123")
WebDriverWait(driver, 5).until(
    lambda d: d.find_element(By.ID, "loginError").text != "")
wait()
shot("exp7_02_invalid_login.png")
login("student1", "pass123")
WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.ID, "studentDashboard")))
fill_leave("2026-11-01", "2026-11-03", "Medical appointment")
wait()
shot("exp7_03_apply_filled.png")
fill_leave("2026-11-05", "2026-11-01", "Medical appointment")
driver.find_element(By.ID, "applyBtn").click()
WebDriverWait(driver, 5).until(
    lambda d: d.find_element(By.ID, "applyError").text != "")
wait()
shot("exp7_04_invalid_dates.png")
driver.refresh()
WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.ID, "studentDashboard")))
fill_leave("2026-11-01", "2026-11-03", "Medical appointment")
driver.find_element(By.ID, "applyBtn").click()
wait(0.7)
shot("exp7_05_pending.png")
driver.find_element(By.ID, "logoutBtn").click()
wait()
login("faculty1", "pass123")
WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.ID, "approverDashboard")))
wait()
driver.find_element(By.CSS_SELECTOR, "button[data-action='approve']").click()
wait()
driver.find_element(By.ID, "logoutBtn").click()
wait()
login("student1", "pass123")
WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.ID, "studentDashboard")))
wait()
shot("exp7_06_approved.png")
def set_mobile(w, h):
    driver.execute_cdp_cmd("Emulation.setDeviceMetricsOverride", {
        "width": w, "height": h, "deviceScaleFactor": 2, "mobile": True})
print("\n=== Experiment 8 (mobile emulation) ===")
reset_app()
set_mobile(390, 844)
wait()
shot("exp8_01_mobile_login.png")
login("student1", "pass123")
WebDriverWait(driver, 5).until(
    EC.visibility_of_element_located((By.ID, "studentDashboard")))
fill_leave("2026-11-01", "2026-11-03", "Medical appointment")
wait()
shot("exp8_02_mobile_form.png")
driver.find_element(By.ID, "applyBtn").click()
wait(0.7)
shot("exp8_03_mobile_list.png")
set_mobile(844, 390)
wait()
shot("exp8_04_mobile_landscape.png")
driver.execute_cdp_cmd("Emulation.clearDeviceMetricsOverride", {})
driver.quit()
print("\nAll screenshots saved to screenshots\\")
