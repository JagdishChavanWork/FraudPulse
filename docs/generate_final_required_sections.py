from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape

DOCS = Path(r'E:\FraudPulse\docs')
OUT = DOCS / 'FinIntel_Input_Output_and_Database_Design.docx'
ER = DOCS / 'generated_report_diagrams' / 'er_diagram.png'
DIAGRAMS = DOCS / 'diagrams'
SCHEMA = Path(r'E:\FraudPulse\database\schema.sql').read_text(encoding='utf-8')

blocks=[]
def p(t='',style=None): blocks.append(('p',t,style))
def h(t): blocks.append(('h',t,None))
def tbl(headers,rows): blocks.append(('table',headers,rows))
def img(path,w,h): blocks.append(('img',str(path),w,h))
def code(t): blocks.append(('code',t,None))

p('FinIntel - Input / Output Screens and Database Design','Title')
p('Focused final document containing UI input screens, output screens, ER diagram, database tables, schema, and data dictionary.','Subtitle')

h('1. Input Screens')
p('1.1 Login Input Screen','Heading2')
p('The login screen allows an authorized employee or analyst to access the FinIntel system using valid employee credentials.')
img(DIAGRAMS / 'Login_page.PNG',610,330)
p('Inputs: Employee ID, Password, Login button.')

p('1.2 Prediction Input Screen','Heading2')
p('The prediction screen allows the analyst to enter applicant, bureau, tradeline, enquiry, customer, and transaction details for credit risk and fraud prediction workflows.')
img(DIAGRAMS / 'Prediction.PNG',610,330)
tbl(['Input Screen','Main Inputs'],[
    ['Login Screen','Employee ID, Password, Login button'],
    ['Credit Risk Prediction Screen','Applicant age, net monthly income, employer tenure, education, gender, marital status, tradelines, enquiries, delinquency values, product enquiry flags'],
    ['Fraud Detection Prediction Screen','Customer age, account type, city tier, account balance, average transaction baseline, transaction amount, transaction type, hour, velocity, anomaly flags'],
    ['Dashboard Filter Screen','Approval flag filters, income range, age range, transaction type, fraud type, risk flag filters'],
])

h('2. Output Screens')
p('2.1 Management Dashboard Output Screen','Heading2')
p('The management dashboard shows portfolio-level KPIs, charts, filtered records, and analytical reports for credit and fraud monitoring.')
img(DIAGRAMS / 'Performance_Dashboard.PNG',610,330)

p('2.2 Detailed Dashboard Output Screen','Heading2')
p('The detailed dashboard output shows extended visual analysis, performance summaries, and filtered decision-support data.')
img(DIAGRAMS / 'performance_dashboard_2.PNG',610,330)

p('2.3 Prediction Output Screen','Heading2')
p('The prediction output screen displays model-generated result, confidence/probability, recommendation, and risk-related details.')
img(DIAGRAMS / 'positive pridection.PNG',610,330)
tbl(['Output Screen','Displayed Output'],[
    ['Credit Risk Prediction Output','Predicted approval category, model confidence, class probabilities, maximum credit amount'],
    ['Fraud Detection Output','Fraud probability, decision threshold, risk level, final verdict, top model signals'],
    ['Credit Dashboard Output','Credit KPIs, approval distribution, income analysis, credit band analysis, filtered records'],
    ['Fraud Dashboard Output','Fraud count, fraud type distribution, transaction summaries, risk breakdown, filtered records'],
])

h('3. Database Design - ER Diagram')
p('The ER diagram represents the main FinIntel database entities and the way employee activity and model predictions are logged.')
img(ER,650,430)

h('4. Database Tables')
tbl(['Table Name','Primary Key','Important Columns','Purpose'],[
    ['employees','id','employee_id, employee_name, employee_password_hash, is_active, created_at, updated_at','Stores employee login and account status.'],
    ['credit_risk_data','id','age, education, gender, marital_status, net_monthly_income, approved_flag, credit_band, max_credit_amount','Stores summarized credit risk records and outcomes.'],
    ['credit_risk_dashboard_enhanced','id','tradeline features, delinquency features, enquiry features, approved_flag, income_bucket, risk_profile','Stores enhanced credit dashboard and model feature records.'],
    ['fraud_detection_data','id','transaction_id, txn_type, txn_amount, anomaly fields, risk_score, risk_band, is_fraud','Stores transaction records and fraud risk output.'],
    ['prediction_logs','id','employee_id, module_name, input_payload, prediction_label, prediction_score, created_at','Stores prediction audit history for credit and fraud modules.'],
])

h('5. Database Schema')
p('Actual schema used by the FinIntel project:')
code(SCHEMA)

h('6. Data Dictionary')
tbl(['Field','Type','Table','Description'],[
    ['id','Integer','All tables','Primary key with auto increment.'],
    ['employee_id','String(30)','employees, prediction_logs','Unique employee identifier and prediction owner reference.'],
    ['employee_name','String(120)','employees','Name of employee or analyst.'],
    ['employee_password_hash','String(255)','employees','bcrypt hashed password.'],
    ['is_active','Boolean','employees','Indicates whether employee can log in.'],
    ['age','Float','credit_risk_data, fraud_detection_data','Applicant/customer age.'],
    ['net_monthly_income','Float','credit tables','Applicant monthly income.'],
    ['approved_flag','String(20)','credit tables','Credit approval class such as P1, P2, P3, P4.'],
    ['credit_band','String(40)','credit_risk_data','Assigned credit band.'],
    ['max_credit_amount','Float','credit_risk_data','Estimated maximum credit amount.'],
    ['transaction_id','String(80)','fraud_detection_data','Unique transaction/case identifier.'],
    ['txn_type','String(40)','fraud_detection_data','Transaction mode such as UPI, NEFT, IMPS, etc.'],
    ['txn_amount','Float','fraud_detection_data','Transaction amount.'],
    ['amount_to_avg_ratio','Float','fraud_detection_data','Transaction amount compared to normal average.'],
    ['balance_drain_pct','Float','fraud_detection_data','Percentage of account balance used by transaction.'],
    ['risk_score','Float','fraud_detection_data','Fraud model risk score.'],
    ['risk_band','String(40)','fraud_detection_data','Low, Medium, or High risk category.'],
    ['is_fraud','Boolean','fraud_detection_data','Fraud classification flag.'],
    ['module_name','String(50)','prediction_logs','Module that generated the prediction.'],
    ['input_payload','Text','prediction_logs','Serialized model input JSON.'],
    ['prediction_label','String(80)','prediction_logs','Prediction output label.'],
    ['prediction_score','Float','prediction_logs','Confidence or probability score.'],
    ['created_at','DateTime','All tables','Record creation timestamp.'],
])

styles='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="34"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:i/><w:sz w:val="23"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="30"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:rPr><w:b/><w:sz w:val="25"/></w:rPr></w:style></w:styles>'''

def para(t='',style=None):
    ppr=f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    return f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{escape(str(t))}</w:t></w:r></w:p>'

def table_xml(headers,rows):
    def cell(t,b=False):
        br='<w:b/>' if b else ''
        return f'<w:tc><w:tcPr><w:tcW w:w="2600" w:type="dxa"/></w:tcPr><w:p><w:r><w:rPr>{br}</w:rPr><w:t xml:space="preserve">{escape(str(t))}</w:t></w:r></w:p></w:tc>'
    out=['<w:tbl><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/><w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/><w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/></w:tblBorders></w:tblPr>']
    out.append('<w:tr>'+''.join(cell(x,True) for x in headers)+'</w:tr>')
    for r in rows: out.append('<w:tr>'+''.join(cell(x) for x in r)+'</w:tr>')
    out.append('</w:tbl>')
    return ''.join(out)

def code_xml(t):
    return ''.join(f'<w:p><w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="16"/></w:rPr><w:t xml:space="preserve">{escape(line)}</w:t></w:r></w:p>' for line in str(t).splitlines())

image_rels=[]; media=[]
def img_xml(path,w,h):
    path=Path(path)
    if not path.exists(): return para(f'[Image missing: {path}]')
    rid=f'rId{len(image_rels)+2}'; ext=path.suffix.lower().replace('.jpeg','.jpg'); name=f'image{len(image_rels)+1}{ext}'
    image_rels.append((rid,name)); media.append((name,path.read_bytes()))
    cx=int(w*9525); cy=int(h*9525)
    return f'''<w:p><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{len(image_rels)}" name="Picture {len(image_rels)}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''

body=[]
for b in blocks:
    if b[0]=='p': body.append(para(b[1],b[2]))
    elif b[0]=='h': body.append(para(b[1],'Heading1'))
    elif b[0]=='table': body.append(table_xml(b[1],b[2]))
    elif b[0]=='img': body.append(img_xml(b[1],b[2],b[3]))
    elif b[0]=='code': body.append(code_xml(b[1]))

document='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>'+''.join(body)+'<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:right="900" w:bottom="900" w:left="900"/></w:sectPr></w:body></w:document>'
content='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Default Extension="jpg" ContentType="image/jpeg"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
rels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
docrels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' + ''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>' for rid,name in image_rels) + '</Relationships>'
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',content); z.writestr('_rels/.rels',rels); z.writestr('word/_rels/document.xml.rels',docrels); z.writestr('word/document.xml',document); z.writestr('word/styles.xml',styles)
    for name,data in media: z.writestr('word/media/'+name,data)
print(OUT)
