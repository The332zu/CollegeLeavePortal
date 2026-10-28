import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pytestmark = pytest.mark.selenium

BASE_URL = os.environ.get("CLP_BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture
def driver():
    d = webdriver.Chrome()
    d.implicitly_wait(2)
    yield d
    d.quit()


def _reset(d):
    d.get(BASE_URL + "/index.html")
    d.execute_script("localStorage.clear();")
    d.refresh()


def test_valid_student_login(driver):
    _reset(driver)
    driver.find_element(By.ID, "username").send_keys("student1")
    driver.find_element(By.ID, "password").send_keys("pass123")
    driver.find_element(By.ID, "loginBtn").click()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "studentDashboard")))


def test_invalid_login_shows_error(driver):
    _reset(driver)
    driver.find_element(By.ID, "username").send_keys("student1")
    driver.find_element(By.ID, "password").send_keys("wrong")
    driver.find_element(By.ID, "loginBtn").click()
    err = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "loginError")))
    assert "Invalid" in err.text


def test_invalid_date_range(driver):
    _reset(driver)
    driver.find_element(By.ID, "username").send_keys("student1")
    driver.find_element(By.ID, "password").send_keys("pass123")
    driver.find_element(By.ID, "loginBtn").click()
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "studentDashboard")))
    driver.execute_script(
        "document.getElementById('startDate').value='2026-11-05';"
        "document.getElementById('endDate').value='2026-11-01';"
        "document.getElementById('reason').value='Medical appointment';")
    driver.find_element(By.ID, "applyBtn").click()
    err = WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.ID, "applyError")))
    assert "before" in err.text