from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from us_states_abbreviations import STATES
from xkcdpass import xkcd_password as xp

import csv


class lamba_is_truthy(object):
    """An "Expected Condition" for use in webdriver waits. Checks that a
    lambda returns a truthy value.
    """

    def __init__(self, truthy_lambda):
        self.truthy_lambda = truthy_lambda

    def __call__(self, driver):
        return self.truthy_lambda(driver)


PASSWORD_KEY = "Password"

# Maps header in CSV file to argument name in
# `enter_new_client_info`. Allows passing row from CSV to
# `enter_new_client_info` as a dict so it can be out of order.
#
CSV_HEADER = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Company Name": "company_name",
    "Email Address": "email",
    "Street1": "address",
    "City": "city",
    "State": "state",
    "Zip": "zip",
    "Main Phone": "phone",

    # custom fields
    "URL": "url",
    "CHECK: Wyoming Network Client": "is_network_client",
    "CSS#": "css_no",
}


def import_csv(im, csv_fname, dry_run=True):
    """
    Import data from 'csv_fname' that has not already been logged to 'log_fname'

    :param WhmcsCsvImporter im:
    :param str csv_fname: input CSV file name
    :param bool dry_run: perform a dry run test (i.e., do not submit new clients)
    :return: same blacklist passed as a param but may have new entries added
    :rtype: dict[str, dict[str, str]]
    """
    dicts = read_csv(csv_fname)
    count = 0
    for row_dict in dicts:
        kw_args = {CSV_HEADER[_key]: row_dict[_key] for _key in CSV_HEADER}
        im.enter_new_client_info(**kw_args)

        # submit new client info
        if not dry_run:
            btn_submit = im.driver.find_element_by_css_selector('input[value="Add Client"]')
            btn_submit.submit()
            WebDriverWait(im.driver, 20).until(
                EC.text_to_be_present_in_element((By.CSS_SELECTOR, "h1"), "Client Profile")
            )
        print('account:\t{}'.format(kw_args['email']))
        im.open_new_client_page()
    print('Import complete')


def open_search_client_page(driver, timeout=20):
    menu = driver.find_element_by_id("Menu-Clients")
    hidden_submenu = driver.find_element_by_id("Menu-Clients-View_Search_Clients")

    actions = webdriver.ActionChains(driver)
    actions.move_to_element(menu)
    actions.move_to_element(hidden_submenu)
    actions.click(hidden_submenu)
    actions.perform()

    # wait for menu to get stale, then wait for next page to complete
    wait_for_staleness(driver, menu)
    wait_for_page_completion(driver, timeout)


def fill_text_input(driver, field_name, field_value):
    elem = driver.find_element_by_name(field_name)
    if field_value:
        elem.clear()
        elem.send_keys(field_value)
    return elem


def search_email(driver, email_address):
    email_field = fill_text_input(driver, "email", email_address)
    email_field.submit()
    wait_for_staleness(driver, email_field)
    wait_for_page_completion(driver)


def read_csv(fname):
    matrix = []
    with open(fname, mode="r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            matrix.append(row)
    return matrix


def wait_for_page_completion(driver, timeout=20):
    wait_until(
        driver,
        lambda browser: browser.execute_script(
            "return document.readyState == 'complete'"
        ),
        timeout,
    )


def wait_for_staleness(driver, element, timeout=20):
    WebDriverWait(driver, timeout).until(EC.staleness_of(element))


def wait_until(driver, lambda_to_invoke, timeout=10):
    wait = WebDriverWait(driver, timeout)
    return wait.until(lamba_is_truthy(lambda browser: lambda_to_invoke(browser)))


class WhmcsCsvImporter(object):

    def cleanup(self):
        self.driver.close()
        self.driver = None

    def login(self, url, username, password):
        self.driver = webdriver.Firefox()  # type: WebDriver
        self.driver.implicitly_wait(20)
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
        elem_submit = self.driver.find_element_by_css_selector(
            'input.btn[type="submit"'
        )
        elem_submit.submit()

        # successful login will implicitly wait and find logout link
        self.driver.find_element_by_id("logout")
        assert self.driver.title == u"WHMCS - Dashboard"

    def logout(self):
        elem_logout = self.driver.find_element_by_id("logout")
        elem_logout.click()

        # implicitly wait for alert to appear
        elem_alert = self.driver.find_element_by_id("alertLoginSuccess")
        assert elem_alert.text == u"You have been successfully logged out."

    def open_new_client_page(self):
        link = self.driver.find_element_by_link_text("Add New Client")
        link.click()
        wait_for_staleness(self.driver, link)
        wait_for_page_completion(self.driver)

    def enter_new_client_info(
            self,
            first_name,
            last_name,
            company_name,
            email,
            address,
            city,
            state,
            zip,
            phone,
            url,
            is_network_client,
            css_no,
    ):
        self._fill_text_input("firstname", first_name)
        self._fill_text_input("lastname", last_name)
        self._fill_text_input("companyname", company_name)
        self._fill_text_input("email", email)

        # password = random_password.make_password()
        password = self.xkcd_password()
        self._fill_text_input("password", password)

        self._fill_text_input("address1", address)
        self._fill_text_input("city", city)
        self._select_state_option("state", state)
        self._fill_text_input("postcode", zip)
        self._fill_text_input("phonenumber", phone)

        self._fill_text_input("notes", "Wyonming Network Client: {}".format(css_no))

        # custom URL, is_Wyoming_network_client, CSS_no
        self._fill_text_input("customfield[5]", url)
        self._check_radio_button("customfield[16]", is_network_client == "Yes")
        self._fill_text_input("customfield[17]", css_no)

        # custom "Payment Method" field
        self._select_dropdown_option("paymentmethod", "WN Import")

        # custom "Client Group" field
        self._select_dropdown_option("groupid", "Wyoming Network Client")

    def xkcd_password(self, num_words=4):
        password = xp.generate_xkcdpassword(xp.generate_wordlist(wordfile=xp.locate_wordfile()), numwords=num_words)
        return password

    def _check_radio_button(self, button_name, should_check):
        cb = self.driver.find_element_by_name(button_name)
        if cb.is_selected():
            if not should_check:
                cb.click()
        else:
            if should_check:
                cb.click()

    def _fill_text_input(self, field_name, field_value):
        if field_value:
            elem = self.driver.find_element_by_name(field_name)
            elem.clear()
            elem.send_keys(field_value)

    def _select_state_option(self, element_name, state_abbrev):
        key = state_abbrev.upper()
        state = STATES[key]
        self._select_dropdown_option(element_name, state)

    def _select_dropdown_option(self, element_name, visible_text):
        elem = self.driver.find_element_by_name(element_name)
        select = Select(elem)
        select.select_by_visible_text(visible_text)


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    csv_fname = sys.argv[4]
    if len(sys.argv) == 6:
        commit = (sys.argv[5] == 'SUBMIT')
    else:
        commit = False

    importer = WhmcsCsvImporter()
    importer.login(url, username, password)
    importer.open_new_client_page()
    import_csv(importer, csv_fname, not commit)
    importer.logout()
    importer.cleanup()
