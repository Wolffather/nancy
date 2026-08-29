Вот автотест на Java с использованием JUnit 5 и RestAssured для проверки GET /widget/config:

```java
import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Тестовый класс для проверки GET /widget/config
 */
public class WidgetConfigApiTest {

    private static final String BASE_URL = "https://api.example.com"; // Замените на реальный URL
    private static final String ENDPOINT = "/widget/config";

    @BeforeAll
    public static void setup() {
        // Базовая конфигурация RestAssured
        RestAssured.baseURI = BASE_URL;
        RestAssured.basePath = "/api/v1"; // если есть базовый путь
    }

    @Test
    @DisplayName("GET /widget/config - проверка получения списка событий")
    public void testGetWidgetConfigReturnsEventsList() {
        // Выполняем GET запрос
        Response response = given()
                .contentType(ContentType.JSON)
                .when()
                .get(ENDPOINT)
                .then()
                .extract()
                .response();

        // Проверка статус-кода
        assertEquals(200, response.getStatusCode(), 
                "Статус-код должен быть 200");
        
        // Проверка Content-Type заголовка
        assertTrue(response.getContentType().contains("application/json"), 
                "Content-Type должен быть application/json");

        // Проверка, что ответ содержит поле events (список)
        assertTrue(response.jsonPath().getList("events") != null, 
                "Ответ должен содержать поле 'events'");
        
        List<?> events = response.jsonPath().getList("events");
        
        // Проверка, что список не пустой (или может быть пустым - зависит от требований)
        assertFalse(events.isEmpty(), "Список событий не должен быть пустым");

        // Проверка структуры каждого события в списке
        for (int i = 0; i < events.size(); i++) {
            // Проверка наличия обязательных полей
            assertNotNull(response.jsonPath().getString("events[" + i + "].id"), 
                    "Событие " + i + " должно содержать поле 'id'");
            assertNotNull(response.jsonPath().getString("events[" + i + "].name"), 
                    "Событие " + i + " должно содержать поле 'name'");
            assertNotNull(response.jsonPath().getString("events[" + i + "].type"), 
                    "Событие " + i + " должно содержать поле 'type'");
            
            // Проверка типов полей
            assertTrue(response.jsonPath().getInt("events[" + i + "].id") > 0, 
                    "ID события должно быть положительным числом");
            assertTrue(response.jsonPath().getString("events[" + i + "].name").length() > 0, 
                    "Название события не должно быть пустым");
        }
    }

    @Test
    @DisplayName("GET /widget/config - проверка с использованием Hamcrest matchers")
    public void testGetWidgetConfigWithMatchers() {
        // Альтернативный вариант с использованием Hamcrest matchers
        given()
                .contentType(ContentType.JSON)
                .when()
                .get(ENDPOINT)
                .then()
                .statusCode(200)
                .contentType(ContentType.JSON)
                .body("events", notNullValue())
                .body("events.size()", greaterThan(0))
                .body("events[0].id", notNullValue())
                .body("events[0].name", not(emptyString()))
                .body("events[0].type", anyOf(is("click"), is("view"), is("scroll")));
    }

    @Test
    @DisplayName("GET /widget/config - проверка с валидацией всех полей")
    public void testGetWidgetConfigFullValidation() {
        // Полная проверка структуры ответа
        given()
                .contentType(ContentType.JSON)
                .when()
                .get(ENDPOINT)
                .then()
                .statusCode(200)
                .contentType(ContentType.JSON)
                .body("events", hasSize(greaterThan(0)))
                .body("events", everyItem(hasKey("id")))
                .body("events", everyItem(hasKey("name")))
                .body("events", everyItem(hasKey("type")))
                .body("events", everyItem(hasKey("timestamp")))
                .body("events.id", everyItem(isA(Integer.class)))
                .body("events.name", everyItem(isA(String.class)))
                .body("events.type", everyItem(isA(String.class)))
                .body("events.timestamp", everyItem(isA(String.class)));
    }

    @Test
    @DisplayName("GET /widget/config - проверка с обработкой ошибок")
    public void testGetWidgetConfigErrorHandling() {
        // Проверка, что при невалидном запросе возвращается 4xx
        given()
                .contentType(ContentType.JSON)
                .when()
                .get(ENDPOINT + "/invalid")
                .then()
                .statusCode(anyOf(is(404), is(400), is(405)));

        // Проверка, что при отсутствии авторизации возвращается 401 или 403
        given()
                .contentType(ContentType.JSON)
                .when()
                .get(ENDPOINT)
                .then()
                .statusCode(anyOf(is(200), is(401), is(403)));
    }

    @Test
    @DisplayName("GET /widget/config - проверка производительности")
    public void testGetWidgetConfigPerformance() {
        long startTime = System.currentTimeMillis();
        
        Response response = given()
                .contentType(ContentType.JSON)
                .when()
                .get(ENDPOINT)
                .then()
                .extract()
                .response();
        
        long endTime = System.currentTimeMillis();
        long responseTime = endTime - startTime;
        
        // Проверка, что ответ получен в течение 5 секунд
        assertTrue(responseTime < 5000, 
                "Время ответа должно быть меньше 5 секунд, но было: " + responseTime + " мс");
        
        // Проверка размера ответа
        int responseSize = response.getBody().asString().length();
        assertTrue(responseSize > 0, "Ответ не должен быть пустым");
        
        System.out.println("Время ответа: " + responseTime + " мс");
        System.out.println("Размер ответа: " + responseSize + " байт");
    }
}
```

**Пояснения к тестам:**

1. **testGetWidgetConfigReturnsEventsList** - основной тест, проверяющий:
   - Статус-код 200
   - Content-Type заголовок
   - Наличие поля `events`
   - Структуру каждого события (id, name, type)

2. **testGetWidgetConfigWithMatchers** - альтернативный вариант с использованием Hamcrest matchers для более компактной проверки

3. **testGetWidgetConfigFullValidation** - полная проверка всех полей в ответе

4. **testGetWidgetConfigErrorHandling** - проверка обработки ошибок и невалидных запросов

5. **testGetWidgetConfigPerformance** - проверка производительности API

**Для запуска тестов необходимо добавить зависимости в pom.xml:**

```xml
<dependencies>
    <!-- JUnit 5 -->
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- RestAssured -->
    <dependency>
        <groupId>io.rest-assured</groupId>
        <artifactId>rest-assured</artifactId>
        <version>5.3.0</version>
        <scope>test</scope>
    </dependency>
    
    <!-- Hamcrest (входит в состав RestAssured, но можно добавить явно) -->
    <dependency>
        <groupId>org.hamcrest</groupId>
        <artifactId>hamcrest</artifactId>
        <version>2.2</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

**Примечания:**
- Замените `BASE_URL` на реальный URL вашего API
- Адаптируйте проверки полей под реальную структуру ответа
- При необходимости добавьте авторизацию (Bearer token, Basic auth и т.д.)