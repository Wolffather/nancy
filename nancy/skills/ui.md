Следуй общим принципам из **best_practices** плюс этим правилам:

## Структура
- Используй Page Object Model для разделения логики страниц и тестов.
- Каждая страница — отдельный класс с локаторами и методами действий.

## Взаимодействие с элементами
- Используй явные ожидания (WebDriverWait) для стабильности.
- Проверяй видимость, наличие, текст, атрибуты элементов.
- Для кликов и ввода используй методы, которые ждут элемент (например, `click()` с ожиданием кликабельности).

## Тестовые данные
- Используй отдельные тестовые данные для каждого теста.
- Очищай данные (например, через API) после теста.

## Скриншоты
- Делай скриншоты при падении теста для упрощения отладки.

## Инструменты
- Для Java: Selenium WebDriver + JUnit.
- Для Python: Selenium + pytest (или Playwright).
- Для JS: Playwright или Cypress.

## Пример кода (Java)
```java
@Test
void should_login_successfully() {
    // given
    LoginPage loginPage = new LoginPage(driver);
    // when
    HomePage homePage = loginPage.login("user", "pass");
    // then
    assertTrue(homePage.isLoggedIn());
}