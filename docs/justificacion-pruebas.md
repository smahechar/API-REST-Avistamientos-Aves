# Justificación de las pruebas: API de avistamientos de aves

**Ingeniería de Software 2 · Taller de pruebas (Sesión 22) · Python + Flask + SQLite**
**Estudiante:** _(nombre)_

**Resumen de la suite:** 94 pruebas (57 unitarias, 37 de integración), todas con nombre de especificación y estructura AAA. Comandos en el `README.md`: `python -m pytest -v` y `python -m pytest --cov --cov-report=term-missing`.

---

## 1. Qué cambió en el código

La API original tenía todo dentro de `crear_app()`: rutas, SQL y validación en una sola función. Para probar la validación había que levantar Flask y crear una base de datos. Separé cuatro responsabilidades:

| Cambio | Antes | Después | Qué se vuelve testeable |
|---|---|---|---|
| **Validación** | función `validar()` anidada en `crear_app`, sin reglas de longitud ni de "no futura" | `validador.py` → `ValidadorDeAvistamiento` | La regla de negocio se prueba como función pura, en milisegundos, sin HTTP ni disco. |
| **Reloj** | (la regla "no posterior a hoy" no existía; implementarla con `date.today()` directo la haría dependiente del día) | `reloj.py` → `RelojDelSistema.hoy()`, inyectado en el validador | Se puede sustituir por un stub (`RelojFijo`) y fijar "hoy". |
| **Acceso a datos** | SQL repartido en cada ruta | `repositorio.py` → `RepositorioSQLite` | El servicio se prueba con un fake en memoria, sin SQLite. |
| **Casos de uso** | lógica mezclada con `request`/`jsonify` | `servicio.py` → `ServicioDeAvistamientos` (lanza `ErrorDeValidacion` / `NoEncontrado`) | El orden de decisiones (p. ej. 404 antes que 400 en PUT) se prueba sin HTTP. |
| **Controlador** | rutas con SQL y validación incrustados | `app.py` delgado: llama al servicio y traduce excepciones a 400/404 mediante `errorhandler` | Lo que queda por probar en HTTP es solo el cableado, y eso lo cubre la integración. |

`crear_app(config, reloj=None)` recibe el reloj como parámetro (inyección de dependencias), de modo que las pruebas de integración fijan la fecha sin tocar el código de producción. El comportamiento externo se conservó: mismas rutas, mismos códigos, y `cargar_ejemplos.py` sigue funcionando. El cuerpo del 400 ahora incluye el campo que falló: `{"campo": "especie", "error": "especie: debe tener entre 3 y 50 caracteres."}`.

**Decisiones de la regla que el enunciado no fijaba:** (a) los textos se normalizan con `strip()` *antes* de medir, para que `"  ab  "` no pase como de 6 caracteres y se guarde de 2; (b) "no posterior a hoy" incluye hoy (`fecha > hoy` es inválida); (c) en `PUT`, un id inexistente responde 404 aunque el cuerpo sea inválido; (d) se reporta el primer campo que falla.

---

## 2. Tabla de casos de la Parte A

Reloj fijo: **hoy = 2026-10-21**. Se escribió antes de programar las pruebas.

### 2.1 Especie (regla: 3 ≤ longitud ≤ 50, medida sin espacios extremos)

Particiones: **P1** longitud < 3 (inválida), **P2** 3 a 50 (válida), **P3** longitud > 50 (inválida), **P4** no es texto / vacía / solo espacios (inválida, otra *razón* de fallo). Los valores límite salen de las fronteras entre P1–P2 y P2–P3.

| Valor | Tipo de caso | Resultado esperado | Por qué este valor y no otro |
|---|---|---|---|
| `"ab"` (2) | Límite (justo bajo el mínimo) | Rechazada, campo `especie` | Frontera P1/P2. Detecta `<` escrito como `<=` en el extremo inferior. |
| `"abc"` (3) | Límite (mínimo válido) | Aceptada | Frontera P1/P2 por el otro lado. |
| `"Tángara multicolor"` (18) | Representativo de P2 | Aceptada | Un valor del interior; además lleva tilde y espacio, como en datos reales. |
| `"a"*50` | Límite (máximo válido) | Aceptada | Frontera P2/P3. |
| `"a"*51` | Límite (justo sobre el máximo) | Rechazada, campo `especie` | Frontera P2/P3 por el otro lado. |
| `"  ab  "` (6 crudos, 2 reales) | Frontera de normalización | Rechazada | Distingue medir antes o después del `strip`. |
| `None`, `""`, `"   "`, `123`, `["garza"]` | Representantes de P4 | Rechazada, campo `especie` | Cada uno es una clase de entrada distinta (ausente, vacía, en blanco, tipo incorrecto). |

No incluí longitudes como 10, 20 y 30: están en la misma partición que `"Tángara multicolor"` y no aportan información nueva.

### 2.2 Fecha (regla: `AAAA-MM-DD`, calendario real, ≤ hoy)

Particiones: **F1** formato incorrecto, **F2** formato correcto pero fecha inexistente, **F3** fecha real ≤ hoy (válida), **F4** fecha real > hoy (inválida), **F5** vacía / no texto. Frontera de valor: hoy / mañana.

| Valor | Tipo de caso | Resultado esperado | Por qué este valor y no otro |
|---|---|---|---|
| `2026-10-21` (hoy) | Límite (máximo válido) | Aceptada | Detecta `>=` en lugar de `>`. |
| `2026-10-22` (mañana) | Límite (mínimo inválido) | Rechazada, campo `fecha` | Frontera F3/F4. |
| `2026-10-20` (ayer) | Representativo de F3 | Aceptada | Confirma que el límite no rompe lo anterior. |
| `2027-01-01` | Representativo de F4 | Rechazada | Mes/día menores que hoy pero año mayor: detecta comparar por partes en vez de la fecha completa. |
| `2024-02-29` | Límite de calendario | Aceptada | 29 de febrero de año bisiesto real. |
| `2025-02-29`, `2026-02-30`, `2026-13-01`, `2026-00-10` | F2 | Rechazada | Formato válido, fecha inexistente: el formato solo no basta. |
| `29-09-2026`, `2026/09/29`, `2026-9-29`, `20260929`, `2026-09-29T10:00`, `ayer` | F1 | Rechazada (mensaje menciona `AAAA-MM-DD`) | Un caso por cada forma de equivocarse: orden, separador, ceros, sin separador, con hora, texto. |
| `None`, `""`, `"  "`, `20260929` | F5 | Rechazada | Entradas de otro tipo que podrían romper el código con una excepción en vez de un 400. |

### 2.3 Lugar y observador

Una sola partición inválida cada uno (ausente / `None` / `""` / solo espacios) y una válida; se prueban con `parametrize` porque la regla es idéntica para ambos campos.

---

## 3. Por qué cada nivel

**Prueba 1: `test_especie_de_51_caracteres_se_rechaza_por_larga` → unitaria.** Verifica una decisión de la lógica (¿51 está fuera de rango?). No necesita HTTP, base de datos ni reloj real: la entrada es un diccionario y la salida es una excepción. Al ser unitaria corre en microsegundos y, si falla, el defecto está en una función de 10 líneas, no en "algo entre la ruta y SQLite". Probar los 12 valores de la tabla por HTTP costaría 12 ciclos de petición + base de datos para obtener la misma información.

**Prueba 2: `test_post_valido_devuelve_201_con_el_cuerpo_y_queda_consultable_por_get` → integración.** Verifica algo que ninguna unitaria puede ver: que las piezas están *conectadas*. **Qué detecta el POST de integración que la unitaria del validador no puede:** (a) que la ruta realmente llame al validador y no se haya olvidado (el validador puede ser perfecto y la API aceptar basura); (b) que `ErrorDeValidacion` se traduzca a 400 y no a 500; (c) que el JSON se serialice con los campos correctos y status 201; (d) que el registro quede persistido en SQLite y un GET posterior lo devuelva (esquema, nombres de columna, `lastrowid`); (e) que el `strip` y el reloj inyectado lleguen hasta el final. Eso son *fronteras* entre componentes, y solo se cruzan de verdad en este nivel.

**Prueba 3: `test_actualizar_un_id_inexistente_lanza_no_encontrado_aunque_los_datos_sean_invalidos` → unitaria del servicio.** La regla es de coordinación (existencia antes que validez), vive en `ServicioDeAvistamientos` y se verifica con el fake del repositorio. Aun así dejé su gemela por HTTP (`test_put_a_id_inexistente_con_cuerpo_invalido_devuelve_404_y_no_400`), porque son *dos riesgos distintos*: la unitaria protege la decisión; la de integración protege que el 404 llegue como código HTTP. Es duplicación deliberada, acotada a un caso.

**Prueba 4: `test_listar_y_resumen_coinciden_entre_implementaciones` → integración (contrato).** Corre el mismo caso contra el fake y contra SQLite real. Es de integración porque toca disco real; su función es garantizar que el doble de la sección 4 no mienta.

---

## 4. Los dobles

| Doble | Tipo | Dónde | Por qué ese tipo |
|---|---|---|---|
| `RelojFijo` | **Stub** | validador, servicio e integración | Solo *entrega* un valor indirecto de entrada (la fecha de hoy). No me interesa verificar que se le llamó; solo que responda siempre lo mismo. |
| `RepositorioEnMemoria` | **Fake** | `test_servicio.py` | Tiene lógica funcional real (dict + ids autoincrementales), así el servicio se prueba por su *estado* (crear → consultar → eliminar → consultar). Un mock obligaría a programar cada respuesta y las pruebas repetirían la implementación. |
| `Mock()` del repositorio | **Mock** | 2 pruebas de `test_servicio.py` | Para el único caso donde lo que importa es un *comportamiento*, no un estado: con datos inválidos, `repositorio.crear` **no** debe llamarse (`assert_not_called`); con datos válidos, se llama una vez con los datos normalizados (`assert_called_once_with`). |

**¿Qué habría pasado sin el doble del reloj?** `ValidadorDeAvistamiento` llamaría a `date.today()`, y la prueba "la fecha de mañana se rechaza" tendría que calcular `hoy + 1`. Peor aún, la prueba del límite "hoy se acepta" sería no determinista alrededor de la medianoche, y no se podría probar "fecha de mañana" con un valor fijo escrito en la tabla. Con `RelojFijo`, "mañana" es siempre `2026-10-22`, hoy y dentro de un año. Se comprueba en `test_el_validador_usa_el_reloj_inyectado_no_el_del_sistema`.

**¿Y sin el fake del repositorio?** Cada prueba del servicio necesitaría un archivo SQLite (más lento, con limpieza de archivos) y, sobre todo, convertiría pruebas de lógica en pruebas de integración disfrazadas: un fallo de SQL aparecería como fallo del servicio.

**Riesgo del fake y cómo se controla:** un fake puede divergir del real. Por eso existe `test_repositorio_contrato.py`: los mismos casos corren contra ambas implementaciones (`params=['memoria', 'sqlite']`).

---

## 5. Lo que no probé (y por qué)

1. **`RelojDelSistema.hoy()`.** Es una línea que delega en `date.today()`. Una prueba solo podría comparar `date.today()` con `date.today()` (tautología) o fallar cerca de la medianoche. El riesgo está en la lógica que *usa* el reloj, y esa sí está cubierta con el stub. Decisión: no vale la pena.
2. **El bloque `if __name__ == '__main__': app.run(debug=True)`.** Arranca un servidor real y bloquea el proceso; probarlo no verifica ninguna regla del negocio. Lo cubre la verificación manual del README (`python app.py`).
3. **Combinaciones de varios campos inválidos a la vez.** Con 4 campos serían 15 combinaciones. El validador reporta solo el primer fallo y cada campo se verifica de forma independiente, así que las combinaciones repiten las pruebas por campo (misma partición, no aporta una clase nueva). Probé en cambio *un* campo inválido a la vez, que es lo que aísla la causa.
4. **Comportamiento propio de Flask** (id no numérico en la ruta, 405) **y de seguridad/carga** (concurrencia, cuerpos gigantes, inyección SQL). Lo primero sería probar el framework, no mi código; lo segundo es otro nivel de prueba, fuera del alcance. Las consultas están parametrizadas (revisado por inspección en `repositorio.py`).
5. **El texto exacto de los mensajes de error.** Verifico el `campo` y que el mensaje lo mencione, no la frase completa: cambiar la redacción no debe romper pruebas sin que haya un defecto.

---

## 6. Lectura de la cobertura

Criterio: **cobertura de sentencias y de ramas** (`branch = True` en `.coveragerc`). Comando: `python -m pytest --cov --cov-report=term-missing`.

```
Name             Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------
app.py              46      1      4      1    96%   69
reloj.py             4      1      0      0    75%   9
repositorio.py      41      0      2      0   100%
servicio.py         24      0      4      0   100%
validador.py        38      0     12      0   100%
------------------------------------------------------------
TOTAL              153      2     22      1    98%
94 passed
```

**Lo que quedó sin cubrir:**

- `app.py:69` (`app.run(debug=True)`) y `reloj.py:9` (`return date.today()`): son exactamente las dos exclusiones 1 y 2 de la sección 5. No hace falta prueba; el número no sube y no pierdo información.
- La **rama parcial** de `app.py` es la misma línea 69 (la condición `__name__ == '__main__'` nunca es verdadera bajo pytest).

**Lo que dice (y lo que no) el 98 %.** Solo dice que el código *se ejecutó*, no que se verificó. Por eso hice una comprobación adicional por **mutación manual**: introduje 5 defectos plausibles y confirmé que la suite falla con cada uno:

| Defecto introducido | ¿Lo detecta la suite? | Prueba que lo mató |
|---|---|---|
| `<=` → `<` en el mínimo de especie | Sí | `especie_de_3_caracteres_se_acepta…` |
| máximo 50 → 51 | Sí | `especie_de_51_caracteres_se_rechaza…` |
| `fecha > hoy` → `fecha >= hoy` | Sí | `fecha_de_hoy_se_acepta…` |
| quitar el `strip()` | Sí | `…normalizado_sin_espacios…` |
| PUT valida antes de verificar existencia | Sí | `actualizar_un_id_inexistente…` |

Los 5 mutantes fueron detectados, lo cual es la evidencia de que los `assert` valen la pena, no solo de que hay líneas ejecutadas. El criterio de ramas, además, confirma que las 12 ramas del validador están ejercitadas, y no solo sus líneas.

**Límite de este análisis:** 5 mutantes hechos a mano no sustituyen una herramienta de mutación (p. ej. `mutmut`); es una muestra dirigida a las fronteras de la tabla de la sección 2.
