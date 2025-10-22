*** Settings ***
Resource  ../resources/browser.resource
Suite Setup  Open Browser Session
Suite Teardown  Close Browser Session
Test Setup  Open Landing Page
Test Teardown  Close Active Page

*** Test Cases ***
Landing Page Displays CTA Buttons
  ${primary_cta}=  Get Text  css=a.btn-primary.btn-lg
  Should Contain  ${primary_cta}  Get Started
  ${secondary_cta}=  Get Text  css=a.btn-outline-primary.btn-lg
  Should Contain  ${secondary_cta}  Login

Register Button Opens Registration Form
  Click  text=Get Started
  Wait For Elements State  css=form#registerForm  state=visible  timeout=5s

Login Link Navigates To Login Form
  Click  a.btn:has-text("Login")
  Wait For Elements State  css=form#loginForm  state=visible  timeout=5s
