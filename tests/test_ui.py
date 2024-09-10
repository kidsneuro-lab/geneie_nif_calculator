import re

import threading
import pytest
from playwright.sync_api import Page, expect

from nif_calculator.app import app

APP_URL = "http://localhost:6001/"

@pytest.fixture(scope="module")
def live_server():
    server = threading.Thread(target=app.run, kwargs={'port': 6001})
    server.daemon = True
    server.start()
    yield
    # Optionally stop the server here, if needed

class TestUIValidScenarios:
    def test_home_page_title(self, live_server, page: Page):
        page.goto(APP_URL)
        expect(page).to_have_title("GENEie NIF Calculator")
        
        # Locate the error message div
        error_message_div = page.locator('#errorMessage')
        
        expect(error_message_div).not_to_be_visible()

        
    def test_sequence_containing_no_motifs(self, live_server, page: Page):
        page.goto(APP_URL)
        page.fill('#sequenceInput', 'AAAAA')
        page.get_by_role(role='button', name='Generate NIF table').click()
        
        table_body = page.locator('#nifTableBody')
        no_data_locator = table_body.locator('tr td.dt-empty')
        expect(no_data_locator).to_contain_text("No data available in table")
        
        # Locate the error message div
        error_message_div = page.locator('#errorMessage')
        
        expect(error_message_div).not_to_be_visible()

    def test_sequence_containing_two_motifs(self, live_server, page: Page):
        page.goto(APP_URL)
        page.fill('#sequenceInput', 'AAAAATTGTAAGAAATCG')
        page.get_by_role(role='button', name='Generate NIF table').click()
        
        table_body = page.locator('#nifTableBody')
        rows = table_body.locator('tr')

        assert rows.count() == 2, f"Expected 2, but got {rows.count()}"
        
        # Validate the content of the first row
        first_row = rows.nth(0)
        expect(first_row.locator('td:nth-child(1)')).to_have_text("3")  # Offset column
        expect(first_row.locator('td:nth-child(2)')).to_have_text("Donor")  # Motif type
        expect(first_row.locator('td:nth-child(3)')).to_have_text("AATTGTAAGAAA")  # Sequence, part of the text is in a span
        expect(first_row.locator('td:nth-child(4)')).to_have_text("0.36")  # U5 column
        expect(first_row.locator('td:nth-child(5)')).to_have_text("0.11")  # U1 column
        expect(first_row.locator('td:nth-child(6)')).to_have_text("0.31")  # U6 column
        expect(first_row.locator('td:nth-child(7)')).to_have_text("")  # A9_A1 column
        expect(first_row.locator('td:nth-child(8)')).to_have_text("")  # A8_E1 column
        expect(first_row.locator('td:nth-child(9)')).to_have_text("")  # A7_E2 column


        # Validate the content of the second row
        second_row = rows.nth(1)
        expect(second_row.locator('td:nth-child(1)')).to_have_text("3")  # Offset column
        expect(second_row.locator('td:nth-child(2)')).to_have_text("Acceptor")  # Motif type
        expect(second_row.locator('td:nth-child(3)')).to_have_text("AATTGTAAGAA")  # Sequence, part of the text is in a span
        expect(second_row.locator('td:nth-child(4)')).to_have_text("")  # U5 column
        expect(second_row.locator('td:nth-child(5)')).to_have_text("")  # U1 column
        expect(second_row.locator('td:nth-child(6)')).to_have_text("")  # U6 column
        expect(second_row.locator('td:nth-child(7)')).to_have_text("0.04")  # A9_A1 column
        expect(second_row.locator('td:nth-child(8)')).to_have_text("0.01")  # A8_E1 column
        expect(second_row.locator('td:nth-child(9)')).to_have_text("0.05")  # A7_E2 column
        
        # Locate the error message div
        error_message_div = page.locator('#errorMessage')
        
        expect(error_message_div).not_to_be_visible()        

class TestUIErrorScenarios:
    def test_invalid_sequence(self, live_server, page: Page):
        page.goto(APP_URL)
        page.fill('#sequenceInput', 'ATCGD')
        page.get_by_role(role='button', name='Generate NIF table').click()
        
        # Locate the error message div
        error_message_div = page.locator('#errorMessage')
        
        expect(error_message_div).to_be_visible()

        expected_error_text = "Error: Sequence must contain only valid nucleotides (A, T, C, G)."
        actual_error_text = error_message_div.inner_text()

        assert actual_error_text == expected_error_text, f"Expected error message: '{expected_error_text}', but found: '{actual_error_text}'"

    def test_empty_sequence(self, live_server, page: Page):
        page.goto(APP_URL)
        page.fill('#sequenceInput', '')
        page.get_by_role(role='button', name='Generate NIF table').click()
        
        # Locate the error message div
        error_message_div = page.locator('#errorMessage')
        
        expect(error_message_div).to_be_visible()

        expected_error_text = "Error: Sequence cannot be empty."
        actual_error_text = error_message_div.inner_text()

        assert actual_error_text == expected_error_text, f"Expected error message: '{expected_error_text}', but found: '{actual_error_text}'"
        
    def test_long_sequence(self, live_server, page: Page):
        page.goto(APP_URL)
        page.fill('#sequenceInput', 'A'*1001)
        page.get_by_role(role='button', name='Generate NIF table').click()
        
        # Locate the error message div
        error_message_div = page.locator('#errorMessage')
        
        expect(error_message_div).to_be_visible()

        expected_error_text = "Error: Sequence must be ≤ 1000 nucleotides in length"
        actual_error_text = error_message_div.inner_text()

        assert actual_error_text == expected_error_text, f"Expected error message: '{expected_error_text}', but found: '{actual_error_text}'"
        