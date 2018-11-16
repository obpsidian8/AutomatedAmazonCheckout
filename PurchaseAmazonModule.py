from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import time
import json
import requests
import re
import traceback
from selenium import webdriver

def add_items_to_cart(driver, url):
    print("Will add items to cart and go to the checkout page.")

    # find and select add to cart button
    invitation = False
    driver.get(url)
    print("\nLooking for add to cart button")
    try:
        addtocart_button = WebDriverWait(driver, 3).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@title="Add to Shopping Cart"]')))
        print("Cart button found.")
        addtocart_button.click()
    except Exception as exc:
        try:
            addtocart_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='add-to-cart-button']")))
            print("Cart button found on 2nd try.")
            addtocart_button.click()
        except Exception as exc:
            print("Might be a invitation")
            try:
                addtocart_button = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[@title='Request an invitation']")))
                print("Request an invitation button found on 3rd try.")
                addtocart_button.click()
                invitation = True
            except Exception as exc:
                print("\nError with add to cart button(2). See message below.")
                print(exc)

    if invitation is True:
        return invitation

    # Taking care of warranty pages - begin
    page_before_check = driver.current_url
    user = ""
    check_pages_and_process(driver, user)

    page_after_check = driver.current_url

    if page_before_check == page_after_check:
        print("second warranty page might be present")
        check_pages_and_process(driver, user)
    else:
        pass
    # Taking care of warranty pages - end

    driver.get('https://www.amazon.com/gp/cart/view.html/ref=lh_cart')


def process_cart_and_checkout(driver, user_account_info, quantity, item_url, item_price):
    current_page = driver.current_url
    if current_page != 'https://www.amazon.com/gp/cart/view.html/ref=lh_cart':
        driver.get('https://www.amazon.com/gp/cart/view.html/ref=lh_cart')
    else:
        print("You're on the cart page")
    # Get number of items in cart.
    item_found_in_cart = 0
    numberIncart = 0
    print("\nChecking if items in cart")
    number_of_executions = 0
    try:
        list_of_cart_items = driver.find_elements_by_xpath('//input[@value="Delete"]')
        print("Items found in cart.")
        item_found_in_cart = 1
        numberIncart = len(list_of_cart_items)
        print("Number of items in cart :" + str(numberIncart))
    except Exception as exc:
        print("No items in cart")

    if numberIncart == 0:
        print("Continuing")
        while number_of_executions <= 2:
            add_items_to_cart(driver, item_url)
            number_of_executions = number_of_executions + 1

    print("Checking out")

    # Check Prices here
    print("Checking prices.")
    order_price_check = check_prices(driver, item_price)

    print("Finding quantity element.")
    qty_element_present = False
    try:
        item_box = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH, '//span[@class="a-button a-button-dropdown a-button-small a-button-span8 quantity"]')))
        print("Quanity element found")
        item_box.click()
        qty_element_present = True
    except Exception as exc:
        print("Error Locating Element..Trying again")

    # ----------------------------------------------------------------------------------------------------------------------
    if qty_element_present == True:
        # Select 10+ from the drop down.
        # print("Selecting 10+ dropdown")
        try:
            ten_plus = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//a[@id="dropdown1_9"]')))
            print("10+ plus element found.")
            # ten_plus.send_keys(quantity)
            ten_plus.click()
            time.sleep(2)
        except Exception as exc:
            print("Error Locating Element...Trying again")

        # ----------------------------------------------------------------------------------------------------------------------

        # Put in the qty limit, hit update and wait for the message to popup
        print("\nFinding qty field element")
        if quantity is None:
            quantity = 1
        try:
            add_item = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                                                                                   '//*[@id="activeCartViewForm"]//div[@class="sc-invisible-when-no-js"]//input[@type="text"]')))
            print("Qty field element found.")
            # add_item.clear()
            time.sleep(2)
            add_item.send_keys(quantity)
        except Exception as exc:
            print("Error Locating qty field:", exc)

        # Update Cart

        print("\nLooking for update cart element")
        try:
            update_cart = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@data-action="update"]')))
            print("Update cart element found.")
            update_cart.click()
            time.sleep(2)
        except Exception as exc:
            print("Cannot locate click button...Trying again")

        # Get quantity alert message
        # Try block here because some items may not have a quantity limit for some sellers

        print("Looking for qty limit alerts at cart page")
        try:
            qty_alert = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.XPATH, '//div[@class="a-alert-content"]//span[@class="a-size-base"]')))
            print("Qty alert found")
            msg = qty_alert.text
            print('Seller Message:' + msg)
        except Exception as ex:
            print(str(ex) + "Trying again")

    print("Checking ite description Kindle or Echo and selecting gift item.")
    item_description_xpath = "//span[@class='a-list-item']//*[contains(@class,'product-link')]//span"
    gift_item_present = False
    try:
        item_description_text = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, item_description_xpath))).text
        description_checker_regex = "(Kindle|Alexa|Echo|Fire)"
        gift_item_keyword = (re.search(description_checker_regex, item_description_text))[0]
        print("Gift item found", gift_item_keyword)
        gift_item_present = True
    except:
        print("No Kindles or Echos or Alexas in this order.")
        gift_item_keyword = ""

    # gift_item_keyword_formatted = (gift_item_keyword.lower()).strip()

    if gift_item_present == True:
        for loop in range(3):
            gift_checkbox_xpath = "//span[@class='a-list-item']//input[@type='checkbox']"
            try:
                gift_item_checkbox = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, gift_checkbox_xpath)))
                gift_item_checkbox.click()
                time.sleep(1)
                print("Gift item checked")
                break
            except:

                if loop == 2:
                    print("Error selecting gift item.")
                    # clear_cart(driver)
                    # return

    print("Proceeding to checkout")
    try:
        proceedToCheckout = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@name='proceedToCheckout']")))
        proceedToCheckout.click()
        time.sleep(1.5)
    except Exception as exc:
        print("\nError with Proceed to checkout button. See message below.")
        print(exc)

    # -------------------------------FINAL CHECKOUT COMMENCING ----------------------------------------------------------------------------#

    check_pages_and_process(driver, user_account_info)

    # shipping options. There are multiple, so essentially trying each one (if they are present. Some sellers only provide the free standard shipping option)
    try:
        two_day_shipping = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'FREE Two-Day Shipping')]]")))
        two_day_shipping.click()
        print("\nFree Two day shipping selected")
    except Exception as exc:
        print("\nFree Two day shipping error")
        print(exc)

        print("\nTrying FREE Regular shipping.")
        try:
            expedited_shipping = WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
                (By.XPATH, "(//span[contains(@class, 'radio-label')]//*[text()[contains(.,'FREE')]])[1]")))
            expedited_shipping.click()
            print("\nFree Shipping selected")
        except Exception as exc:
            print("\nFree Shipping selected")
            print(exc)

            print("\nTrying Free Standard shipping")
            try:
                standard_shipping = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'FREE Shipping')]]")))
                standard_shipping.click()
                print("\nStandard Shipping Selected ")
            except Exception as exc:
                print("\nShipping selection error. See message below.See message below")
                print(exc)



    print("\nChecking prices again at final checkout.\nGetting spc-orders text")
    try:
        message_body_field_message = driver.find_element_by_xpath('//div[@id="spc-orders"]').text
    except:
        print("Copy Page fail")
        message_body_field_message = "Nothing...:-("

    print("Working on body text")
    print("Getting price at checkout")
    price_checkout = ""
    price_checkout_regex = re.compile(r"^\$[\s\S]*?([\d,.]+)[\s\S]*?(Quantity|Qty)", flags=re.MULTILINE)
    try:
        price_checkout_text = (price_checkout_regex.search(message_body_field_message).group(1)).strip()
        print(f"Price at Checkout: {price_checkout_text}")
        price_checkout = float(price_checkout_text)
    except Exception as exc:
        print(f"Error {exc}")

    if type(price_checkout) is float:
        if price_checkout <= item_price:
            print(f"Price Checkout {price_checkout}")
            print(f"Final Deal Price {item_price}")
            print("price check passed")
            order_price_check = True
        else:
            print(f"Price Checkout {price_checkout}")
            print(f"Final Deal Price {final_price}")
            print("price check failed")
            order_price_check = False



    if order_price_check == True:
        # Finally, place order. This is the final page in the checkout process
        orderplaced = 0
        try:
            placeYourOrder1 = WebDriverWait(driver, 6).until(
                EC.element_to_be_clickable((By.XPATH, "(//input[@name='placeYourOrder1'])[3]")))
            time.sleep(1)
            placeYourOrder1.click()
            orderplaced = 1
        except Exception as exc:
            try:
                placeYourOrder1 = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@name='placeYourOrder1']")))
                time.sleep(1)
                print("Submit order button found.")
                placeYourOrder1.click()
                time.sleep(1)
                orderplaced = 1
            except:
                orderplaced = 0
                print("\nError placing order. See message below")
                print(exc)

        time.sleep(1)
        if orderplaced == 1:
            print("\nOrder was placed.")
            print("Looking for order confirmation page")
            try:
                order_confirmation = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[contains(@id,'order-number')]"))).text
                print("Order Number:" + order_confirmation + " " + str(user_account_info['Account']))
                msg = "Amazon.com " + order_confirmation + " " + str(user_account_info['Account']) + ", " + str(user_account_info['Username'])
                notifier_auto_purchase(msg)
            except:
                print("Error getting order confirmation")
        else:
            print("No confirmation page because order was not placed.")
    else:
        msg = f"Prices do not match for Amazon item "
        print(msg)
        notifier_script_run_monitor(msg)
        notifier_auto_purchase(msg)
        clear_cart(driver)

        time.sleep(15)
        return None


def check_prices(driver, final_price):
    print("\nFUNC: \"check_prices\"")
    # This is called from final page
    print("\nGetting cart price for items")
    print("Final deal Price,", final_price)
    try:
        cart_Price_element = driver.find_element_by_xpath(
            "//*[@id='activeCartViewForm']//span[@class='cart-pmp-discount a-text-bold']").text
        cart_Price_element_comma = (cart_Price_element.replace('$', ''))
        cart_Price = float(cart_Price_element_comma.replace(',', ''))
        print("Cart Total Price:", cart_Price)
    except Exception as exc:
        try:
            cart_Price_element = driver.find_element_by_xpath(
                "//span[@class='a-size-medium a-color-price sc-price sc-white-space-nowrap sc-product-price sc-price-sign a-text-bold']").text
            cart_Price_element_comma = (cart_Price_element.replace('$', ''))
            cart_Price = float(cart_Price_element_comma.replace(',', ''))
            print("Cart Total Price:", cart_Price)
        except Exception as exc:
            print("\nError getting total cart price")
            print(exc)
            cart_Price = 1.00

    try:
        if cart_Price <= final_price:
            print("Price check passed.")
            return True
        else:
            print("Price Check Failed")
            return False
    except Exception as exc:
        print("Error processing check_prices comparison")
        return True


def logout_user(driver):
    print("\nFUNC: \"logout_user\"")
    print("Logging out any previous sessions.")
    # Fetching this URL is equivalent to logging out. Another option is to click the logout button.
    driver.get(
        'https://www.amazon.com/gp/flex/sign-out.html/ref=nav_youraccount_bnav_ya_ad_so?ie=UTF8&action=sign-out&path=%2Fgp%2Fyourstore%2Fhome&signIn=1&useRedirectOnSuccess=1')
    return None


def login_user(driver, user):
    print("Logging in user")
    driver.get('https://www.amazon.com/gp/your-account/order-history?ref_=ya_d_c_yo')

    page_title = driver.title
    login_alert_present = False

    if page_title == 'Amazon Sign In':
        print("You are on the login page.")

        print("Logging in current user.")
        try:
            # You many be presented with one of 2 different kinds of pages
            addAccount = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Add account')]")))
            addAccount.click()
        except:
            print("Add account element not present. Looking for email field")

        alternate_login = False
        try:
            email_field = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='email']")))
            email_field.clear()
            time.sleep(1)
            email_field.send_keys(user['Username'])
        except:
            print("\nError! Email field not present.")
            alternate_login = True
            try:
                password_field = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
                password_field.clear()
                password_field.send_keys(user['UserPwd'])
                time.sleep(2)
            except:
                print("\nPassword field not found.")

        if alternate_login is False:

            try:
                continue_button = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@id='continue']")))
                continue_button.click()
            except:
                print("\nUh-oh. Continue button not found.")

            try:
                password_field = WebDriverWait(driver, 2).until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='password']")))
                password_field.clear()
                password_field.send_keys(user['UserPwd'])
                time.sleep(2)
            except:
                print("\nPassword field not found.")

        try:
            submit_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@id='signInSubmit']")))
            submit_button.click()
        except:
            print("\nCannot find submit button.")

        # See if any alerts exits after hitting the submit button
        try:
            login_alert_ele = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='a-box-inner a-alert-container']")))
            login_alert_present = True
            print("\nUser not loggged in.")
        except Exception as exc:
            print("\nUser logged in. See message.")
            print(exc)
            login_alert_present = False

        # Alert exists, print a the message.
        if login_alert_present == True:
            try:
                login_alert_msg = WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[@class='a-box-inner a-alert-container']//span[@class='a-list-item']"))).text
                print(login_alert_msg)
                msg = "User not logged in. " + login_alert_msg + " for " + user['Username']
                notifier_auto_purchase(msg)
                notifier_script_run_monitor(msg)
            except Exception as exc:
                print(exc)

    else:
        print("You are not on the login page.")

    return login_alert_present


def clear_cart(driver):
    # you should be logged in to the account when this is called.

    print("Clearing cart.")

    # Go to Cart page and delete items from the cart.
    driver.get('https://www.amazon.com/gp/cart/view.html/ref=lh_cart')

    # Get number of items in cart.
    try:
        list_of_cart_items = driver.find_elements_by_xpath('//input[@value="Delete"]')
        numberIncart = len(list_of_cart_items)
        print("\nNumber of items in cart :" + str(numberIncart))
    except:
        print("No items found in cart")
        numberIncart = 0

    for item in range(0, (numberIncart)):
        try:
            itemTodelete = driver.find_element_by_xpath('//input[@value="Delete"]')
            itemTodelete.click()
            time.sleep(2)
        except Exception as e:
            print("Error with delete button. Details :\n" + str(e))

    try:
        shopping_cart_empty = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.XPATH, "//div[@class='a-row sc-cart-header']//h1"))).text
        print("Cart Text: ", shopping_cart_empty)
    except:
        print("\nItems reamining in shopping cart")

    print("\nEnd")
    return None


def notifier_script_run_monitor(msg):
    # You can send messages to slack if you have a slack account
    try:
        webhook_url = 'your slack webhook url goes here'
        slack_data = {'text': msg, "channel": "#script_run_monitor"}
        response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s' % (response.status_code, response.text))
    except:
        print("Error sending run notification")


def notifier_auto_purchase(response):
    # You can send messages to slack if you have a slack account
    try:
        webhook_url = 'your slack webhook url goes here'
        slack_data = {'text': response, "channel": "#auto-purchase"}

        response = requests.post(webhook_url, data=json.dumps(slack_data), headers={'Content-Type': 'application/json'})
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s' % (response.status_code, response.text))
    except:
        print("Error sending run notification")


def check_pages_and_process(driver, user):
    print("checking page before process.")
    before_url = driver.current_url
    before_page_title = driver.title

    if before_page_title == 'Amazon Sign In':
        print("You're on login page.\nCalling login function.")
        try:
            # Call external function to login at this point if you have to
            login_user(driver, user)
        except Exception as exc:
            print("Error logging in while trying to proceed to checkout")
            print(exc)

    elif 'https://www.amazon.com/gp/buy/spc/handlers/display.html?hasWorkingJavascript=1' in before_url:
        print("You're on final page.")
        return




    elif 'product' in before_url or '/dp/' in before_url:
        print("Warranty page appeared after clicking add to cart.")
        # Click No thanks. Case insensitive Xpath
        no_thanks_xpath = "(//text()[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'no thanks')]/../..)"
        page_before_click = driver.title
        try:
            number_of_elements_no_thanks = driver.find_elements_by_xpath(no_thanks_xpath)
            number_of_cont_buttons = len(number_of_elements_no_thanks)
        except:
            number_of_cont_buttons = 5
        for i in range(1, number_of_cont_buttons + 1):
            try:
                continue_from_no_thanks = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, no_thanks_xpath + "[" + str(i) + "]")))
                time.sleep(1)
                continue_from_no_thanks.click()
                time.sleep(1)
                page_after_click = driver.title
                if page_after_click != page_before_click:
                    break
            except Exception as exc:
                close_dialog_xpath = '(//button[@data-action = "a-popover-close"])'
                try:
                    continue_from_no_thanks = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, close_dialog_xpath + "[" + str(i) + "]")))
                    time.sleep(1)
                    continue_from_no_thanks.click()
                    time.sleep(1)
                    page_after_click = driver.title
                    if page_after_click != page_before_click:
                        break
                except Exception as exc:
                    print("error: continue_from_no_thanks")
                    print(exc)


    elif 'Select a Payment Method' in before_page_title or 'payselect' in before_url:
        # Click continue after selecting shipping
        select_cc_xpath = '//*[@id="existing-credit-cards-box"]//div[@data-a-input-name]'
        try:
            select_cc = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, select_cc_xpath)))
            select_cc.click()
            time.sleep(1)
        except Exception:
            print("\nError selecting cc. See message below")
            traceback.print_exc()
            print("error: select_cc")

        continue_from_payselect_xpath = "((//span[@class='a-button-inner']//*[text()[contains(.,'Use this payment')]])/..)"
        page_before_click = driver.title
        try:
            number_of_elements_ship_cont = driver.find_elements_by_xpath(continue_from_payselect_xpath)
            number_of_cont_buttons = len(number_of_elements_ship_cont)
        except:
            number_of_cont_buttons = 5
        for i in range(1, number_of_cont_buttons + 1):
            try:
                continue_from_payselect = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, continue_from_payselect_xpath + "[" + str(i) + "]")))
                time.sleep(1)
                continue_from_payselect.click()
                time.sleep(1)
                page_after_click = driver.title
                if page_after_click != page_before_click:
                    break
            except Exception as exc:
                use_this_payment_xpath = "(//span[@class='a-button-inner']//*[text()[contains(.,'Use this payment')]])[1]/.."
                try:
                    use_this_payment_button = WebDriverWait(driver, 2).until(
                        EC.element_to_be_clickable((By.XPATH, use_this_payment_xpath)))
                    use_this_payment_button.click()
                    time.sleep(1)
                except Exception as exc:
                    use_this_payment_xpath = '//*[@id="continue-bottom"]'
                    try:
                        use_this_payment_button = WebDriverWait(driver, 1).until(
                            EC.element_to_be_clickable((By.XPATH, use_this_payment_xpath)))
                        use_this_payment_button.click()
                        time.sleep(1)
                    except Exception as exc:
                        print("\nError selecting default address. See message below")
                        print(exc)
                        print("error: continue_from_payselect")


    elif 'Select Shipping Options' in before_page_title or 'shipoptionselect' in before_url:
        print("need to select shipping options")
        try:
            two_day_shipping = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'FREE Shipping')]]")))
            two_day_shipping.click()
            print("\nFree Two day shipping selected")
        except Exception as exc:
            print("\nFree Two day shipping error")
            print(exc)

            print("\nTrying FREE Regular shipping.")
            try:
                expedited_shipping = WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
                    (By.XPATH, "(//span[contains(@class, 'radio-label')]//*[text()[contains(.,'FREE')]])[1]")))
                expedited_shipping.click()
                print("\nFree Shipping selected")
            except Exception as exc:
                print("\nFree Shipping selected")
                print(exc)

                print("\nTrying Free shipping")
                try:
                    standard_shipping = WebDriverWait(driver, 1).until(
                        EC.element_to_be_clickable((By.XPATH, "//*[text()[contains(.,'FREE Two-Day Shipping')]]")))
                    standard_shipping.click()
                    print("\nStandard Shipping Selected ")
                except Exception as exc:
                    print("\nShipping selection error. See message below.See message below")
                    print(exc)

        time.sleep(1)
        # Click continue after selecting shipping
        continue_from_shipping_xpath = "//input[@value='Continue']"
        page_before_click = driver.title
        try:
            number_of_elements_ship_cont = driver.find_elements_by_xpath(continue_from_shipping_xpath)
            number_of_cont_buttons = len(number_of_elements_ship_cont)
        except:
            number_of_cont_buttons = 5
        for i in range(1, number_of_cont_buttons + 1):
            try:
                continue_from_shipoptionselect = WebDriverWait(driver, 6).until(
                    EC.element_to_be_clickable((By.XPATH, continue_from_shipping_xpath + "[" + str(i) + "]")))
                time.sleep(1)
                continue_from_shipoptionselect.click()
                time.sleep(1)
                page_after_click = driver.title
                if page_after_click != page_before_click:
                    break
            except Exception as exc:
                print("error: continue_from_shipoptionselect")


    elif before_page_title == 'Choose gift options' or 'gift' in before_url:
        save_gift_options_xpath = '//*[@id="giftForm"]/div[1]/div[2]/div/span[1]/span/input'
        print("Saving gift options ")
        try:
            save_gift_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, save_gift_options_xpath)))
            save_gift_button.click()
        except:
            print("Error saving fit items.")

    elif before_page_title == 'Select a shipping address' or 'addressselect' in before_url:
        print("need to select address")
        try:
            defaultAddress = WebDriverWait(driver, 2).until(EC.element_to_be_clickable(
                (By.XPATH, "//span[@class='a-button-inner']//*[text()[contains(.,'Deliver to this address')]]")))
            defaultAddress.click()
            time.sleep(1)
        except Exception as exc:
            try:
                defaultAddress = WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
                    (By.XPATH, "(//span[@class='a-button-inner']//*[text()[contains(.,'Use this address')]])[1]/..")))
                defaultAddress.click()
                time.sleep(1)
            except Exception as exc:
                print("\nError selecting default address. See message below")
                print(exc)


    elif before_page_title == 'Business Order Information':
        try:
            skip_businessOrder_information = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@class='a-button-input']")))
            skip_businessOrder_information.click()
        except Exception as exc:
            print("\nError logging on business order page. See message below")
            print(exc)



    elif "Edit Quantities - Amazon.com Checkout" in before_page_title:
        print("Looking for qty limit errors")
        try:
            qty_limit_error = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//input[@class='a-button-input']"))).text
            msg = str(user['Account']) + " Error " + str(qty_limit_error)
            notifier_auto_purchase(msg)
            notifier_script_run_monitor(msg)
        except:
            try:
                qty_limit_error = WebDriverWait(driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                " //*[@id='changeQuantityFormId']//div[@class='a-row a-spacing-small a-spacing-top-mini']"))).text
                msg = str(user['Account']) + " Error " + str(qty_limit_error)
                notifier_auto_purchase(msg)
                notifier_script_run_monitor(msg)
            except:
                try:
                    qty_limit_error = WebDriverWait(driver, 1).until(EC.element_to_be_clickable(
                        (By.XPATH, "//*[@id='changeQuantityFormId']/table[2]/tbody/tr/td/div/div"))).text
                    msg = str(user['Account']) + " Error " + str(qty_limit_error)
                    notifier_auto_purchase(msg)
                    notifier_script_run_monitor(msg)
                except:
                    print("No qty limit errors found")

        msg = "Amazon Message: We're sorry. \"This item has limited purchase quantity. We have changed your purchase quantity to the maximum allowable\". "
        msg2 = str(user['Account']) + " " + msg
        print(msg2)
        notifier_auto_purchase(msg2)
        notifier_script_run_monitor(msg2)

        continue_shared_xpath = '//*[@id="changeQuantityFormId"]//input[@value="Continue"]'
        try:
            continue_shared_button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((By.XPATH, continue_shared_xpath)))
            continue_shared_button.click()
            time.sleep(1)
        except:
            print("error: continue_shared_button ")

    else:
        pass

    time.sleep(0.5)
    print("Checking page after process.")
    after_url = driver.current_url
    after_page = driver.title

    if (after_url != before_url) or (after_page != before_page_title):
        print("Processing done. New page. Process new page.")
        check_pages_and_process(driver, user)
    else:
        print("No processing (could be) done. Same page. Return.")
        return


def SetupChrome():
    """Sets up a new data directory and profile for chrome separate from your regular browser profile."""

    path_to_dir = "C:/Chromeprofiles"
    profile_folder = "Ultron"
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--user-data-dir=' + path_to_dir)
    chrome_options.add_argument('--profile-directory=' + profile_folder)

    print("\nSetting Chrome Options.")
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.set_window_size(1200, 2000)
    return driver


def main_purchase_process(item_url, quantity, item_price, user_account_info):
    msg = f"Beginning Amazon Checkout for Amazon account {user_account_info['Username']}"
    print(msg)

    driver = SetupChrome()
    driver.set_window_size(1200, 2000)

    # Try to login and see if there are any issues with logging in
    login_issue = login_user(driver, user_account_info)
    if not login_issue:
        # Clear cart of any previous items that are in there before beginning a new purchase.
        clear_cart(driver)

        request_invitation = add_items_to_cart(driver, item_url)
        if (request_invitation is False) or (request_invitation is None):
            process_cart_and_checkout(driver, user_account_info, quantity, item_url, item_price)

        print("Closing out browser sessions")
        driver.close()
        driver.quit()
    else:
        driver.close()
        driver.quit()



# This is the main function.
def PurchaseAmazon():
    print("\nReading Item Checkout Information.")
    item_checkout_information = json.load(open('Item_Checkout_Information.json'))

    item_url = item_checkout_information['item_url']
    quantity = item_checkout_information['quantity']
    item_price = item_checkout_information['item_price']


    print("\nReading user accounts.")
    users_list = json.load(open('Amazon_Account_Information.json'))


    # Will perform check process for accounts in user accounts file.
    for user_account_info in users_list:
        main_purchase_process(item_url, quantity, item_price, user_account_info)


print("\nEnd of Processing")

if __name__ == '__main__':
    PurchaseAmazon()
