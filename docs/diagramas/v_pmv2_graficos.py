import json, csv, datetime as dt
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
M=json.load(open('/home/claude/TP_RAG_Quechua/backend/modelos/metricas.json'))
AZ='#1F3864'; AC='#8A5A2B'; GR='#9A9A9A'
# ROC both
fig,axs=plt.subplots(1,2,figsize=(10,4.3),dpi=200)
for ax,k,t in [(axs[0],'cobertura','Predicción 1 · cobertura documental'),(axs[1],'pasajes','Predicción 2 · relevancia de pasajes')]:
    r=M[k]['roc']; auc=M[k]['metadatos']['validacion_cruzada']['auc_roc']
    ax.plot(r['fpr'],r['tpr'],color=AC,lw=2.2,label=f'Regresión logística (AUC {auc:.3f})')
    ax.plot([0,1],[0,1],'--',color=GR,lw=1,label='Azar (AUC 0,5)')
    if k=='cobertura':
        b=M[k]['linea_base_regla_umbral']; ax.scatter([1-b['especificidad']],[b['sensibilidad']],color=AZ,zorder=5,s=40,label='Regla del PMV1 (τ + lema)')
    else:
        b=M[k]['linea_base_regla_palabras']; ax.scatter([1-b['especificidad']],[b['sensibilidad']],color=AZ,zorder=5,s=40,label='Regla del PMV1 (2 palabras)')
        pe=M[k]['punto_elegido']; ax.scatter([pe['falsos_positivos_F']],[pe['cobertura_E']],color='#2F6B3A',marker='D',zorder=6,s=40,label='Regla + modelo (corte 0,5)')
    ax.set_title(t,fontsize=11,color=AZ,fontweight='bold'); ax.set_xlabel('Tasa de falsos positivos'); ax.set_ylabel('Sensibilidad')
    ax.legend(fontsize=8,loc='lower right'); ax.grid(alpha=.25); ax.set_xlim(-.02,1.02); ax.set_ylim(-.02,1.02)
fig.tight_layout(); fig.savefig('ml_roc.png')
# comparison bars
fig,axs=plt.subplots(1,2,figsize=(10,3.8),dpi=200)
nombres={'regresion_logistica':'Reg. logística','bosque_aleatorio':'Bosque aleatorio','linea_base_mayoritaria':'Clase mayoritaria','regla_umbral_pmv1':'Regla PMV1','regla_palabras_pmv1':'Regla PMV1'}
for ax,k in [(axs[0],'cobertura'),(axs[1],'pasajes')]:
    comp=M[k]['metadatos']['comparacion']
    ks=list(comp); x=range(len(ks))
    f1=[comp[c]['f1'] for c in ks]; auc=[comp[c]['auc_roc'] or 0 for c in ks]
    ax.bar([i-.2 for i in x],auc,.4,color=AZ,label='AUC-ROC'); ax.bar([i+.2 for i in x],f1,.4,color=AC,label='F1')
    for i,(a,f) in enumerate(zip(auc,f1)):
        ax.text(i-.2,a+.01,f'{a:.2f}',ha='center',fontsize=7.5); ax.text(i+.2,f+.01,f'{f:.2f}',ha='center',fontsize=7.5)
    ax.set_xticks(list(x)); ax.set_xticklabels([nombres[c] for c in ks],fontsize=8.5); ax.set_ylim(0,1.12)
    ax.set_title('Predicción 1 · cobertura (n = 415)' if k=='cobertura' else 'Predicción 2 · pasajes (n = 167)',fontsize=10.5,color=AZ,fontweight='bold')
    ax.legend(fontsize=8,loc='lower left'); ax.grid(axis='y',alpha=.25)
fig.tight_layout(); fig.savefig('ml_comparacion.png')
# coefficients
fig,axs=plt.subplots(1,2,figsize=(10,4),dpi=200)
for ax,k in [(axs[0],'cobertura'),(axs[1],'pasajes')]:
    c=M[k]['metadatos']['coeficientes']; it=sorted(c.items(),key=lambda x:x[1])
    ax.barh([a for a,_ in it],[b for _,b in it],color=[AC if b>0 else GR for _,b in it])
    ax.set_title('Coeficientes · '+('cobertura' if k=='cobertura' else 'pasajes'),fontsize=10.5,color=AZ,fontweight='bold'); ax.tick_params(labelsize=7.5); ax.axvline(0,color='#333',lw=.8); ax.grid(axis='x',alpha=.25)
fig.tight_layout(); fig.savefig('ml_coeficientes.png')
# transactions latency hist
lat=[float(r['latencia_ms']) for r in csv.DictReader(open('/home/claude/TP_RAG_Quechua/docs/evidencias/pmv2/transacciones.csv'))]
latp=[float(r['latencia_ms']) for r in csv.DictReader(open('/home/claude/TP_RAG_Quechua/docs/evidencias/pmv2/postgres/transacciones.csv'))]
fig,ax=plt.subplots(figsize=(8,3.4),dpi=200)
ax.hist(lat,bins=40,alpha=.75,color=AZ,label=f'SQLite · 800 transacciones'); ax.hist(latp,bins=40,alpha=.55,color=AC,label='PostgreSQL + procedimientos · 1000')
ax.set_xlabel('Latencia del caso de uso completo (ms)'); ax.set_ylabel('Transacciones'); ax.legend(fontsize=8.5); ax.grid(alpha=.25)
ax.set_title('Prueba con data masiva: distribución de la latencia',fontsize=11,color=AZ,fontweight='bold')
fig.tight_layout(); fig.savefig('transacciones_latencia.png')
# Gantt
D=lambda s: dt.date(2026,int(s[3:5]),int(s[:2]))
filas=[('PMV1 · Sprint 1 (S1–S3)','08-09','29-09','08-09','01-10'),
('PMV1 · Sprint 2 (S4–S6)','29-09','20-10',None,None),
('PMV2 · Sprint 3 · analítica predictiva','20-10','10-11','20-10','29-10'),
('PMV3 · Sprint 4 · app móvil','10-11','01-12','21-09','22-09'),
('Transversal · documentación','08-09','01-12','08-09','29-10')]
fig,ax=plt.subplots(figsize=(10,3.6),dpi=200)
for i,(n,b0,b1,e0,e1) in enumerate(filas[::-1]):
    ax.barh(i+.18,(D(b1)-D(b0)).days,left=D(b0),height=.32,color='white',edgecolor=AZ,hatch='///',label='Línea base (Documento 4)' if i==0 else None)
    if e0: ax.barh(i-.18,(D(e1)-D(e0)).days or 1,left=D(e0),height=.32,color=AC,label='Ejecutado' if i==0 else None)
ax.set_yticks(range(len(filas))); ax.set_yticklabels([f[0] for f in filas[::-1]],fontsize=8.5)
ax.axvline(D('29-10'),color='#2F6B3A',lw=1.5); ax.text(D('29-10'),3.55,' 29-10\n entrega S11',color='#2F6B3A',fontsize=8,va='center')
ax.text(D('29-09'),3-.18,'  integrado y adelantado en el Sprint 1 (CHG: un PMV = un sprint)',fontsize=7.5,va='center',color=AC)
ax.text(D('23-09'),1-.18,'  adelantado: índice exportado y app sin red (repo móvil)',fontsize=7.5,va='center',color=AC)
import matplotlib.dates as md; ax.xaxis.set_major_formatter(md.DateFormatter('%d-%m')); ax.grid(axis='x',alpha=.25)
ax.set_title('Diagrama de Gantt: línea base frente a lo ejecutado',fontsize=11,color=AZ,fontweight='bold')
ax.legend(fontsize=8,loc='lower right'); fig.tight_layout(); fig.savefig('gantt.png')
print('ok')
