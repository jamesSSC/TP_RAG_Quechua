/// Lo que estiman los dos modelos predictivos del PMV2 para una consulta, sin responderla.
///
/// Prediccion 1: probabilidad de respaldo documental (HU-08.1, RF-14, corte 0,25).
/// Prediccion 2: probabilidad de que los pasajes de prosa traten la pregunta (HU-04, RF-15,
/// corte 0,50). Ambas son regresiones logisticas sobre caracteristicas estandarizadas.
class PrediccionMl {
  const PrediccionMl({
    required this.texto,
    required this.probabilidadCobertura,
    required this.corteCobertura,
    required this.probabilidadPasajes,
    required this.cortePasajes,
    this.decisionCobertura,
    this.decisionPasajes,
    this.bloquearia = false,
    this.caracteristicas = const {},
    this.pesosCobertura = const {},
  });

  final String texto;
  final double? probabilidadCobertura;
  final double corteCobertura;
  final double? probabilidadPasajes;
  final double cortePasajes;
  final String? decisionCobertura;
  final String? decisionPasajes;

  /// Por debajo del corte el sistema se abstendria aunque la similitud lo permitiera.
  final bool bloquearia;

  /// Valor de cada variable que recibio el modelo para esta consulta.
  final Map<String, double> caracteristicas;

  /// Coeficiente estandarizado de cada variable en el modelo de cobertura: cuanto y en que
  /// sentido empuja la probabilidad. Es el peso de la variable en el modelo, no su
  /// contribucion exacta a esta consulta (para eso haria falta la media y la desviacion del
  /// estandarizador, que la API no expone).
  final Map<String, double> pesosCobertura;
}
