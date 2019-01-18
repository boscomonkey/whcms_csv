from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver


class WhcmsCsvImporter(object):

    def __init__(self):
        self.driver = webdriver.Firefox()  # type: WebDriver
        self.driver.implicitly_wait(20)

    def cleanup(self):
        self.driver.close()
        self.driver = None

    def login(self, url, username, password):
        self.driver.get(url)

        # enter username
        elem_user = self.driver.find_element_by_css_selector('input[name="username"]')
        elem_user.clear()
        elem_user.send_keys(username)

        # enter password
        elem_pass = self.driver.find_element_by_css_selector('input[name="password"]')
        elem_pass.clear()
        elem_pass.send_keys(password)

        # submit
        elem_submit = self.driver.find_element_by_css_selector('input.btn[type="submit"')
        elem_submit.submit()

        # successful login will implicitly wait and find logout link
        self.driver.find_element_by_id('logout')
        assert self.driver.title == u'WHMCS - Dashboard'

    def logout(self):
        elem_logout = self.driver.find_element_by_id('logout')
        elem_logout.click()

        # implicitly wait for alert to appear
        elem_alert = self.driver.find_element_by_id('alertLoginSuccess')
        assert elem_alert.text == u'You have been successfully logged out.'

    def new_client(self):
        menu = self.driver.find_element_by_id('Menu-Clients')
        hidden_submenu = self.driver.find_element_by_id('Menu-Clients-Add_New_Client')

        actions = webdriver.ActionChains(self.driver)
        actions.move_to_element(menu)
        actions.move_to_element(hidden_submenu)
        actions.click(hidden_submenu)
        actions.perform()

        # implicitly wait for firstname to appear
        self.driver.find_element_by_name('firstname')


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    importer = WhcmsCsvImporter()
    importer.login(url, username, password)
    importer.new_client()
    importer.logout()
    importer.cleanup()
