from draw import *
fig,ax=canvas(16,9.2)
ax.text(8,8.95,'Diagrama de paquetes UML — arquitectura hexagonal en cuatro capas (backend/src)',fontsize=14,fontweight='bold',color=AZ,ha='center',va='center')
# infrastructure
pkg(ax,4.2,7.25,7.6,1.05,'infrastructure','#FDECEA',tabw=1.7)
box(ax,4.4,7.38,2.3,0.78,'config.py\nτ = 0,48 · cortes ML · BD',bold_first=True)
box(ax,6.85,7.38,2.3,0.78,'contenedor.py\ncomposition root (DI)',bold_first=True)
box(ax,9.3,7.38,2.3,0.78,'main.py\nFastAPI en 127.0.0.1',bold_first=True)
# adapters in
pkg(ax,0.25,2.55,3.3,3.85,'adapters/in','#FFF6E5',tabw=1.7)
box(ax,0.45,4.55,2.9,1.65,'rest/\nConsultas · Historial\nFuentes · Corpus\nSistema · Prediccion (PMV2)',bold_first=True,fs=8.8)
box(ax,0.45,3.6,2.9,0.75,'cli/\nindexar · evaluar · medir',bold_first=True,fs=8.8)
box(ax,0.45,2.7,2.9,0.72,'scripts/\nentrenar_predictores · transacciones',bold_first=True,fs=8.8)
# application
pkg(ax,4.2,2.55,7.6,3.85,'application','#EAF3FB',tabw=1.7)
pkg(ax,4.4,3.0,2.25,2.9,'ports/in','#F7FBFF',fs=9.5,tabw=1.0)
box(ax,4.5,3.12,2.05,2.6,'«interface»\nConsultarCorpusPort\nPredecirConsultaPort\nAnalizarDemandaPort\nIngestarDocumentoPort\nGestionarFuentesPort\nConsultarHistorialPort\nReindexarCorpusPort',fs=8.2)
pkg(ax,6.95,3.0,2.1,2.9,'use_cases','#F7FBFF',fs=9.5,tabw=1.15)
box(ax,7.05,3.12,1.9,2.6,'ConsultarCorpus\nPredecirConsulta\nAnalizarDemanda\nIngestarDocumento\nGestionarFuentes\nConsultarHistorial\nReindexarCorpus',fs=8.0)
pkg(ax,9.35,3.0,2.3,2.9,'ports/out','#F7FBFF',fs=9.5,tabw=1.1)
box(ax,9.45,3.12,2.1,2.6,'«interface»\nIndiceRecuperacionPort\nGeneradorTextoPort\nPredictorPort\nTraductorPort\nDetectorIdiomaPort\nExtraccionDocumentalPort\nRepositorioCorpusPort\nRepositorioFuentesPort\nRepositorioConsultasPort',fs=7.8)
# adapters out
pkg(ax,12.45,2.55,3.3,3.85,'adapters/out','#FFF6E5',tabw=1.8)
outs=[('recuperacion/','IndiceHibridoLexico'),('generacion/','OllamaGenerador · Literal'),('prediccion/','PredictorSklearn'),('traduccion/','TraductorTabla · OllamaTraductor'),('documentos/','ExtractorPdf · CorpusJsonl'),('persistencia/','SQLAlchemy · Postgres (SP)')]
for i,(a,b) in enumerate(outs):
    box(ax,12.6,5.62-i*0.58,3.0,0.5,f'{a}\n{b}',bold_first=True,fs=7.9)
# domain
pkg(ax,4.2,0.3,7.6,1.65,'domain  — solo biblioteca estándar','#E8F5E9',tabw=3.6)
box(ax,4.4,0.45,2.3,1.3,'entities/\nConsulta · Fragmento\nFuente · Respuesta\nFragmentoRecuperado',bold_first=True,fs=8.2)
box(ax,6.85,0.45,2.3,1.3,'value_objects/\nIdioma · Procedencia\nPuntuacionSimilitud\nUmbral',bold_first=True,fs=8.2)
box(ax,9.3,0.45,2.3,1.3,'services/\nEvaluadorConfianza\nDepuradorConsulta\nCaracteristicasConsulta',bold_first=True,fs=8.0)
# arrows
arrow(ax,(5.0,7.25),(2.4,6.7),'«ensambla»',dashed=True)
arrow(ax,(11.0,7.25),(13.6,6.7),'«ensambla»',dashed=True)
arrow(ax,(3.45,4.6),(4.5,4.6),'invoca',loff=(0,0.2))
arrow(ax,(7.0,4.95),(6.55,4.95),'implementa',dashed=True,loff=(0,0.22),fs=7.8)
arrow(ax,(8.95,4.95),(9.45,4.95),'usa',loff=(0,0.2))
arrow(ax,(12.6,4.1),(11.55,4.1),'implementa',dashed=True,loff=(0,0.22),fs=7.8)
arrow(ax,(8.0,2.55),(8.0,1.97),'usa',loff=(0.35,0))
# legend
ax.text(0.3,1.6,'→  dependencia\n⇢  realización / ensamblado\nLas dependencias apuntan\nsiempre hacia el dominio.',fontsize=8.6,va='center',color='#333333',linespacing=1.5)
ax.text(12.5,1.2,'Estructura real de backend/src\nen la rama feat/pmv2-prediccion-ml.',fontsize=8.2,va='center',color='#8B2E2E',style='italic',linespacing=1.4)
fig.savefig('v_paquetes.png',dpi=200); print('ok')
