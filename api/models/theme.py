from pydantic import BaseModel


class ThemeModel(BaseModel):
    bodyText: str = '#8f9498'
    buttonBackground: str = '#192733'
    buttonText: str = '#ffffff'
    footerBackground: str = '#22619c'
    footerText: str = '#323a5d'
    formBackground: str = '#ffffff'
    formBorder: str = '#a7b0b3'
    formText: str = '#32385d'
    headerBackground: str = '#2852a2'
    imageBackground: str = '#324d5d'
    imageText: str = '#32445d'
    linkText: str = '#3a60d0'
    navBackground: str = '#212225'
    navText: str = '#ffffff'
    pageBackground: str = '#e8e8e8'
    pageText: str = '#26292b'
    saleText: str = '#32465d'
    titleText: str = '#25524f'
