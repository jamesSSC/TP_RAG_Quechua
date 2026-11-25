# Asistente de consulta del quechua wanka — aplicación móvil

Aplicación Android que consulta el corpus documental publicado sobre el quechua wanka de
Junín en **dos modos** (ADR-038 del proyecto):

- **En línea (principal):** cliente de la API desplegada (`https://quechua-api.onrender.com`), con
  los mismos endpoints públicos que la web: respuesta con cita, abstención, pasajes, predicción ML y
  fuentes del corpus.
- **Sin conexión (respaldo):** todo se resuelve en el dispositivo con el índice exportado y el
  compositor determinista. Ninguna consulta sale del teléfono.

En automático la app usa la nube y pasa sola al corpus del teléfono si no hay red, si la API no
responde en 20 s o si devuelve un 5xx. También hay un selector manual. El modo activo se ve siempre
en la cabecera y cada respuesta dice de qué modo vino. Ante un 429 muestra la espera que pide el
servidor y no reintenta sola. La app no lleva tokens ni funciones de administración.

Es el incremento móvil del proyecto (PMV3). El backend, la web y la documentación viven en
[TP_RAG_Quechua](https://github.com/omarpiero/TP_RAG_Quechua), y de ahí salen los artefactos que
esta aplicación empaqueta.

## Qué hace

Responde a la equivalencia de una palabra del español o del inglés en quechua wanka,
citando siempre el documento y la página de los que sale. **No traduce frases**: cuando no
hay respaldo documental lo dice en lugar de proponer una forma inventada, que es la
salvaguarda central del proyecto.

Las consultas en inglés pasan por el español antes de buscar, porque el corpus está
indexado en español: `love` → `amor` → `Kuyay`.

Ante una pregunta de gramática no afirma nada: entrega los pasajes del corpus, literales y
citados, para que los juzgue quien consulta.

## Cómo resuelve sin modelo

| Pieza | Cómo |
|---|---|
| Recuperación | TF-IDF léxico exportado desde el escritorio; el dispositivo solo hace el producto punto |
| Traducción inglés→español | Tabla de 2257 lemas calculada una sola vez, 177 KB |
| Redacción de la respuesta | Compositor determinista sobre la entrada de diccionario |
| Historial | SQLite local |

No hay ningún modelo de lenguaje embarcado. La medición de viabilidad determinó que
ninguno que quepa en un teléfono lee una entrada lexicográfica con fidelidad: uno de
0,8 B llegó a afirmar que *ashuti* significa «uña», y uno de 2 B invirtió la
correspondencia de *agua*. El compositor determinista acertó las 180 de 180 consultas del
conjunto de evaluación.

## Cifras medidas

| | |
|---|---|
| Paquete de instalación release (arm64-v8a / armeabi-v7a / x86_64) | 22,6 / 20,2 / 24,0 MB |
| Índice completo empaquetado | 12 MB, 3605 fragmentos |
| Arranque en frío (`am start -W`, profile) | 682–788 ms; índice listo en 140–175 ms |
| Consulta sin conexión, 248 consultas | P50 0,80 ms · P95 2,71 ms |
| Arnés de 248 consultas en el dispositivo | recall@5 1,000 en A, B y D; 0 falsos positivos en C |

Medido en emulador x86_64 (Pixel 9 Pro, API 37) el 20/11/2026. Estas cifras **no sirven para
declarar requisitos no funcionales**: para eso hay que medir en un dispositivo ARM real. La
instrumentación se lee con `adb logcat | grep MEDICION` en compilaciones debug y profile.

## Arquitectura

Hexagonal, igual que el escritorio:

```
lib/
  dominio/          entidades, objetos de valor y los puertos (consulta, modo, preferencias)
  aplicacion/       depurador, evaluador de confianza, compositor, detector de idioma
  infraestructura/  contenedor y adaptadores: AsistenteNube, AsistenteLocal, AsistenteConmutado,
                    HistorialSqlite, índice portable y tabla de traducción
  presentacion/     pantalla principal, vistas (consultar, fuentes, predicción ML) y componentes
```

La pantalla solo conoce `AsistentePort`. Lo cumplen tres adaptadores y el contenedor inyecta
`AsistenteConmutado`, que compone la nube y el corpus local. Así se pasó de una app solo sin
conexión a una de dos modos sin tocar el dominio ni la lógica del modo sin conexión.

## Ejecutar

```bash
flutter pub get
flutter run -d <dispositivo>
# Otra API (p. ej. el backend local desde el emulador):
flutter run --dart-define=API_URL=http://10.0.2.2:8000
```

Para compilar el paquete de instalación:

```bash
flutter build apk --release --split-per-abi
```

## Pruebas

```bash
flutter test                                                        # 45 pruebas, sin red
flutter test integration_test/arnes_dispositivo_test.dart -d <id>   # 248 consultas en el dispositivo
```

Las pruebas de interfaz y de adaptadores usan un doble de la API, así que no necesitan la nube.
`test/seguridad_test.dart` falla si alguien añade un token o una escritura contra la nube.

Incluye una prueba de paridad que compara el motor de puntuación del dispositivo con el de
scikit-learn sobre quince consultas escogidas por lo que ponen a prueba: acentos y ñ,
coincidencia de lema por debajo del umbral, términos que solo casan por n-gramas de
caracteres, prosa, inglés, consultas fuera de cobertura y una consulta que es solo fraseo.
La diferencia máxima admitida es el redondeo de precisión simple, porque cualquier
desviación mayor desplazaría el umbral calibrado, que es lo que impide que el sistema
proponga formas no documentadas.

## Actualizar el índice

Los archivos de `assets/indice/` se generan desde el backend del proyecto:

```bash
python backend/scripts/exportar_indice_movil.py <carpeta>
python backend/scripts/validar_indice_movil.py
```

y se copian a `assets/indice/`. El umbral de abstención viaja en `manifiesto.json` junto
al índice, para que no pueda quedar desincronizado del ajuste con el que se calculó.

## Alcance

Herramienta de consulta sobre fuentes documentales ya publicadas. No sustituye la
validación por hablantes de la comunidad ni se constituye en autoridad lingüística sobre
la variedad wanka.
