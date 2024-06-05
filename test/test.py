from pages.page import page


def test_get_all_dropdown_elements():
    t = page('firefox')
    t.navigate_to('http://sandbox-auto/')
    elements = t.get_all_dropdown_elements_list(page.SelectPais)
    print("Cant: ", len(elements))
    i = 0
    for e in elements:
        i = i + 1
        # print("País:" + str(e.text) + str(i))
    t.sleep(6)
    t.close_browser()


if __name__ == "__main__":
    # test_upload_file_sandbox()
    test_get_all_dropdown_elements()
    # pytest -s test.py::test_wait_for_element_to_disappear
