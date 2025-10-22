*** Settings ***
Library  Browser
Library  OperatingSystem

*** Variables ***
${BASE_URL}    http://localhost:8000
${BROWSER}    chromium

*** Keywords ***
Initialize Variables
  ${url}=  Get Environment Variable  BASE_URL   default=http://localhost:8000
  ${bro}=  Get Environment Variable  BROWSER   default=chromium
  VAR   ${BASE_URL}   ${url}   scope=GLOBAL
  VAR  ${BROWSER}   ${bro}   scope=GLOBAL

Open Browser Session
  Initialize Variables
  New Browser  browser=${BROWSER}  headless=${TRUE}

Close Browser Session
  Close Browser

Open Landing Page
  New Page  ${BASE_URL}/

Close Active Page
  Close Page
