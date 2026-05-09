from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
from PIL import Image, ImageDraw, ImageFont
import shutil

DOCS = Path(r'E:\FraudPulse\docs')
DIAG = DOCS / 'generated_report_diagrams'
OUT = DOCS / 'FinIntel_Project_Documentation.docx'
DIAG.mkdir(parents=True, exist_ok=True)

try:
    FONT = ImageFont.truetype('arial.ttf', 18)
    FONT_B = ImageFont.truetype('arialbd.ttf', 20)
    FONT_H = ImageFont.truetype('arialbd.ttf', 26)
    FONT_S = ImageFont.truetype('arial.ttf', 15)
except Exception:
    FONT = FONT_B = FONT_H = FONT_S = ImageFont.load_default()


def wrap(text, width):
    words = str(text).split()
    lines, line = [], ''
    for w in words:
        test = (line + ' ' + w).strip()
        if len(test) <= width:
            line = test
        else:
            if line: lines.append(line)
            line = w
    if line: lines.append(line)
    return lines


def box(draw, xy, text, fill='#f7fbff', outline='#315f7d', font=None):
    x1,y1,x2,y2 = xy
    draw.rounded_rectangle(xy, radius=12, fill=fill, outline=outline, width=2)
    use_font = font or FONT
    lines = wrap(text, max(12, int((x2-x1)/10)))
    total_h = len(lines)*20
    y = y1 + ((y2-y1)-total_h)/2
    for line in lines:
        line_font = FONT_B if len(lines)==1 and font is None else use_font
        bbox = draw.textbbox((0,0), line, font=line_font)
        draw.text((x1+(x2-x1-(bbox[2]-bbox[0]))/2, y), line, fill='#173244', font=line_font)
        y += 20


def table_card(draw, xy, title_text, fields, fill='#f7fbff', outline='#315f7d'):
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=12, fill=fill, outline=outline, width=2)
    draw.rectangle((x1, y1, x2, y1 + 42), fill=outline)
    bbox = draw.textbbox((0, 0), title_text, font=FONT_B)
    draw.text((x1 + (x2 - x1 - (bbox[2] - bbox[0])) / 2, y1 + 10), title_text, fill='white', font=FONT_B)
    y = y1 + 58
    for field in fields:
        draw.text((x1 + 16, y), field, fill='#173244', font=FONT_S)
        y += 24


def arrow(draw, start, end, fill='#263238'):
    draw.line([start, end], fill=fill, width=3)
    ex,ey = end; sx,sy = start
    import math
    ang = math.atan2(ey-sy, ex-sx)
    l = 12
    pts = [(ex,ey), (ex-l*math.cos(ang-0.45), ey-l*math.sin(ang-0.45)), (ex-l*math.cos(ang+0.45), ey-l*math.sin(ang+0.45))]
    draw.polygon(pts, fill=fill)


def title(draw, text, w):
    bbox = draw.textbbox((0,0), text, font=FONT_H)
    draw.text(((w-(bbox[2]-bbox[0]))/2, 20), text, fill='#0f2f3f', font=FONT_H)


def save_system_usecase(path):
    W,H=1400,850; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'System Use Case Diagram - FinIntel',W)
    box(d,(40,350,230,455),'Risk Analyst','#fff8e8','#9b6b00')
    cases=[('Login',430,110),('View Management Insights',760,110),('Run Credit Risk Prediction',430,310),('Run Fraud Detection Prediction',760,310),('View Reports',430,510),('Logout',760,510)]
    for text,x,y in cases: box(d,(x,y,x+250,y+95),text)
    box(d,(1130,240,1350,350),'Database','#f1fff2','#2e7d32')
    box(d,(1130,460,1350,570),'ML Models','#fff1f1','#9f3434')
    for _,x,y in cases: arrow(d,(230,402),(x,y+48))
    for text,x,y in cases[1:5]: arrow(d,(x+250,y+48),(1130,295 if 'Prediction' not in text else 515))
    im.save(path)


def save_module_usecase(path):
    W,H=1500,950; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'Module-wise Use Case Diagram',W)
    modules=[('Authentication',['Enter credentials','Verify active employee','Create session','Logout'],60),('Management Insights',['Open dashboard','Apply filters','View charts','View data tables'],430),('Credit Risk Prediction',['Enter applicant details','Build feature payload','Predict approval class','Estimate max amount','Log prediction'],800),('Fraud Detection Prediction',['Enter transaction details','Calculate anomaly signals','Predict fraud probability','Display verdict','Log prediction'],1170)]
    for name,items,x in modules:
        d.rounded_rectangle((x,100,x+300,870),radius=16,fill='#f8fafc',outline='#627d98',width=2)
        box(d,(x+25,125,x+275,190),name,'#eaf5ff','#315f7d')
        y=245
        prev=None
        for item in items:
            box(d,(x+45,y,x+255,y+70),item,'#ffffff','#607d8b')
            if prev: arrow(d,(x+150,prev+70),(x+150,y))
            prev=y; y+=120
    im.save(path)


def save_er(path):
    W,H=1700,1100; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'ER Diagram - FinIntel Database',W)
    cards = {
        'employees': (90, 140, 455, 355),
        'prediction_logs': (675, 430, 1045, 705),
        'credit_risk_data': (90, 675, 455, 920),
        'credit_risk_dashboard_enhanced': (1235, 120, 1645, 410),
        'fraud_detection_data': (1235, 675, 1645, 950),
    }
    table_card(d, cards['employees'], 'employees', [
        'PK id', 'UK employee_id', 'employee_name', 'employee_password_hash',
        'is_active', 'created_at', 'updated_at'
    ], '#fffdf7', '#8a5b00')
    table_card(d, cards['prediction_logs'], 'prediction_logs', [
        'PK id', 'FK employee_id', 'module_name', 'input_payload',
        'prediction_label', 'prediction_score', 'created_at'
    ], '#f4f9ff', '#315f7d')
    table_card(d, cards['credit_risk_data'], 'credit_risk_data', [
        'PK id', 'age, education, gender', 'net_monthly_income',
        'approved_flag', 'credit_band', 'max_credit_amount', 'created_at'
    ], '#f8fff9', '#2e7d32')
    table_card(d, cards['credit_risk_dashboard_enhanced'], 'credit_risk_dashboard_enhanced', [
        'PK id', 'tradeline features', 'delinquency features', 'enquiry features',
        'approved_flag', 'income_bucket', 'risk_profile', 'created_at'
    ], '#f8fff9', '#2e7d32')
    table_card(d, cards['fraud_detection_data'], 'fraud_detection_data', [
        'PK id', 'UK transaction_id', 'txn_type, txn_amount',
        'anomaly features', 'risk_score', 'risk_band', 'is_fraud', 'created_at'
    ], '#fff7f7', '#9f3434')
    arrow(d, (455, 248), (675, 520)); d.text((500, 330), '1 employee creates many logs', font=FONT, fill='#334')
    arrow(d, (455, 805), (675, 630)); d.text((490, 730), 'credit prediction logged', font=FONT, fill='#334')
    arrow(d, (1235, 265), (1045, 520)); d.text((1055, 350), 'enhanced credit prediction logged', font=FONT, fill='#334')
    arrow(d, (1235, 805), (1045, 630)); d.text((1055, 730), 'fraud prediction logged', font=FONT, fill='#334')
    im.save(path)


def save_activity(path):
    W,H=1300,1050; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'Activity Diagram',W)
    steps=[('Start',560,90),('Open Streamlit App',520,180),('Login / Authenticate',510,290),('Select Module from Sidebar',490,410),('Dashboard / Credit / Fraud Workflow',450,535),('Run Query or ML Prediction',490,660),('Display Result and Report',500,785),('Save Prediction Log',515,895)]
    prev=None
    for text,x,y in steps:
        box(d,(x,y,x+300,y+70),text,'#f8fff9','#2e7d32' if text in ['Start'] else '#315f7d')
        if prev: arrow(d,(prev[0]+150,prev[1]+70),(x+150,y))
        prev=(x,y)
    im.save(path)


def save_sequence(path):
    W,H=1500,900; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'Sequence Diagram - Prediction Flow',W)
    actors=[('Analyst',120),('Streamlit UI',390),('Auth Module',660),('Database',930),('ML Model',1200)]
    for name,x in actors:
        box(d,(x-90,100,x+90,155),name,'#fff','#315f7d'); d.line((x,155,x,820),fill='#9aa',width=2)
    msgs=[(120,390,210,'enter credentials'),(390,660,285,'verify password'),(660,930,360,'fetch employee'),(930,660,435,'employee record'),(390,120,510,'show app'),(120,390,585,'submit form'),(390,1200,660,'request prediction'),(1200,930,735,'save prediction log'),(390,120,800,'display label and confidence')]
    for sx,ex,y,text in msgs:
        arrow(d,(sx,y),(ex,y)); d.text(((sx+ex)/2-70,y-24),text,font=FONT_S,fill='#333')
    im.save(path)


def save_class(path):
    W,H=1550,900; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'Class Diagram - Database Models',W)
    classes=[('Employee\n-id:int\n-employee_id:str\n-employee_name:str\n-is_active:bool',70,140),('PredictionLog\n-id:int\n-employee_id:str\n-module_name:str\n-input_payload:text\n-prediction_score:float',600,320),('CreditRiskData\n-id:int\n-income:float\n-approved_flag:str\n-credit_band:str',70,580),('CreditRiskDashboardEnhanced\n-id:int\n-bureau_features\n-approved_flag:str\n-risk_profile:str',1080,140),('FraudDetectionData\n-id:int\n-transaction_id:str\n-risk_score:float\n-is_fraud:bool',1080,580)]
    for text,x,y in classes: box(d,(x,y,x+360,y+190),text.replace('\\n','\n'),'#fdfdfd','#37474f')
    arrow(d,(430,235),(600,410)); arrow(d,(430,675),(600,470)); arrow(d,(1080,235),(960,410)); arrow(d,(1080,675),(960,470))
    im.save(path)


def save_hierarchy(path):
    W,H=1450,950; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'Module Hierarchy Diagram',W)
    box(d,(600,80,850,145),'app.py','#eaf5ff','#315f7d')
    top=[('config',150),('database',420),('modules',690),('ml',960),('models/data',1230)]
    for name,x in top:
        box(d,(x,250,x+180,315),name); arrow(d,(725,145),(x+90,250))
    subs={'database':['connection.py','models.py','seed.py'], 'modules':['auth','common','dashboard','prediction','services'], 'ml':['credit_risk','credit_limit','fraud']}
    for name,x in top:
        y=430
        for s in subs.get(name,[]):
            box(d,(x-15,y,x+195,y+55),s,'#fff','#607d8b'); arrow(d,(x+90,315),(x+90,y)); y+=90
    im.save(path)

paths = {
 'er': DIAG/'er_diagram.png', 'system': DIAG/'system_usecase.png', 'module': DIAG/'module_usecase.png',
 'activity': DIAG/'activity.png', 'sequence': DIAG/'sequence.png', 'class': DIAG/'class.png', 'hierarchy': DIAG/'hierarchy.png'
}
save_er(paths['er']); save_system_usecase(paths['system']); save_module_usecase(paths['module']); save_activity(paths['activity']); save_sequence(paths['sequence']); save_class(paths['class']); save_hierarchy(paths['hierarchy'])

blocks=[]
def p(t='',style=None): blocks.append(('p',t,style))
def h(level,t): blocks.append(('h',t,level))
def tbl(headers,rows): blocks.append(('table',headers,rows))
def img(path,w=620,h=360): blocks.append(('img',str(path),w,h))
def code(t): blocks.append(('code',t,None))

p('FinIntel Project Documentation','Title')
p('Actual diagrams, database design, UI/output documentation, limitations, test cases, and sample code.','Subtitle')
h(1,'1.3 Operating Environment Hardware and Software')
tbl(['Category','Specification'],[['Client','Modern browser on Windows/Linux/macOS, 4 GB RAM minimum.'],['Server','Streamlit Cloud or equivalent Linux runtime, 2 GB+ RAM recommended for model loading.'],['Runtime','Python 3.10 environment.'],['Database','SQLite for local/demo; PostgreSQL or compatible SQL database through DATABASE_URL for production.'],['Network','Internet required for cloud deployment and remote access.']])
h(1,'1.4 Brief Description about Technology Used')
tbl(['Technology','Purpose'],[['Python','Application, ML, data processing, and backend logic.'],['Streamlit','Interactive web UI, forms, dashboards, tabs, sidebar navigation.'],['pandas / NumPy','Dataframe processing and feature preparation.'],['scikit-learn / XGBoost','Model pipelines, classifiers, regressors, and predictions.'],['SQLAlchemy','Database ORM, models, sessions, and queries.'],['bcrypt','Secure password hashing.'],['Plotly / Altair / Matplotlib / Seaborn','Charts and analytical reports.'],['joblib','Loading trained ML model artifacts.']])
h(1,'2.1 Proposed System')
p('FinIntel is a banking risk intelligence system for analyst-assisted decision support. It combines employee login, management dashboards, credit risk prediction, maximum credit amount estimation, fraud prediction, and prediction audit logging.')
h(1,'2.2 Module Specifications / Scope')
tbl(['Module','Scope'],[['Authentication','Employee login, active employee validation, bcrypt password verification, session handling, logout.'],['Management Insights','Credit risk and fraud dashboards with filters, KPIs, charts, and data tables.'],['Credit Risk Prediction','Applicant/bureau inputs, approval category prediction, maximum credit amount estimation, probability output, log storage.'],['Fraud Detection Prediction','Transaction inputs, anomaly feature calculation, fraud probability, risk level, verdict, log storage.'],['Database Layer','SQLAlchemy models for employees, credit datasets, fraud datasets, and prediction logs.'],['ML Layer','joblib model loading, payload preparation, predictions, metrics, and trained artifacts.']])
h(1,'2.3 Objectives of System')
tbl(['Objective No.','Objective'],[['1','Provide secure access for banking analysts.'],['2','Display credit and fraud insights through dashboards.'],['3','Predict applicant approval category and credit amount.'],['4','Detect suspicious transactions using ML-based probability.'],['5','Maintain prediction history for audit and review.'],['6','Support local and Streamlit Cloud deployment.']])
h(1,'3.1 ER Diagram'); img(paths['er'],650,430)
h(1,'3.2 Use Case Diagram - System Use Case Diagram'); img(paths['system'],650,395)
h(1,'3.2.1 Use Case Diagram - Module-wise Use Case'); img(paths['module'],650,410)
h(1,'3.3 Activity Diagram'); img(paths['activity'],580,470)
h(1,'3.4 Sequence Diagram'); img(paths['sequence'],650,390)
h(1,'3.5 Class Diagram'); img(paths['class'],650,380)
h(1,'3.6 Module Hierarchy Diagram'); img(paths['hierarchy'],650,420)
h(1,'3.7 Table Specifications - Database Design')
tbl(['Table','Primary Key','Important Fields','Purpose'],[['employees','id','employee_id, employee_name, employee_password_hash, is_active, created_at, updated_at','Stores employee login and status details.'],['credit_risk_data','id','age, education, gender, net_monthly_income, approved_flag, credit_band, max_credit_amount','Stores credit risk records and credit outcomes.'],['credit_risk_dashboard_enhanced','id','tradeline metrics, delinquency metrics, enquiries, approved_flag, income_bucket, risk_profile','Stores enhanced dashboard and credit model feature data.'],['fraud_detection_data','id','transaction_id, txn_type, txn_amount, risk_score, risk_band, is_fraud','Stores transaction and fraud analysis data.'],['prediction_logs','id','employee_id, module_name, input_payload, prediction_label, prediction_score, created_at','Stores audit trail for prediction submissions.']])
h(1,'3.8 Data Dictionary')
tbl(['Field','Data Type','Description'],[['employee_id','String(30)','Unique employee login ID.'],['employee_password_hash','String(255)','bcrypt password hash.'],['net_monthly_income','Float','Applicant monthly income.'],['approved_flag','String(20)','Approval class such as P1, P2, P3, P4.'],['credit_band','String(40)','Credit band assigned to applicant.'],['max_credit_amount','Float','Estimated maximum credit amount.'],['transaction_id','String(80)','Unique transaction case ID.'],['txn_amount','Float','Transaction amount.'],['amount_to_avg_ratio','Float','Transaction amount compared with normal average.'],['balance_drain_pct','Float','Percentage of account balance used by transaction.'],['risk_score','Float','Fraud model risk score.'],['risk_band','String(40)','Low, Medium, or High risk classification.'],['is_fraud','Boolean','Fraud flag result.'],['input_payload','Text','JSON input submitted to prediction model.'],['prediction_score','Float','Confidence or probability score.']])
h(1,'4.1 User Interface Screens - Input')
tbl(['Screen','Actual Inputs'],[['Login','Employee ID, password, login button.'],['Credit Risk Prediction','Applicant age, net monthly income, employer tenure, education, gender, marital status, tradelines, enquiries, delinquency fields, product enquiry fields, loan flags.'],['Fraud Detection Prediction','Customer age, account type, city tier, account tenure, balance, average spend, transaction type, transaction amount, hour, day, velocity, anomaly flags.'],['Management Insights','Credit dashboard tab, fraud dashboard tab, approval filters, income range, age range, transaction type filters, fraud type filters.']])
h(1,'4.2 Output Screens with Data')
tbl(['Screen','Actual Output'],[['Credit Risk Prediction','Predicted approval category, model confidence percentage, maximum credit amount, class probability table.'],['Fraud Detection Prediction','Fraud probability, decision threshold, risk level badge, final verdict, amount-to-average ratio, balance drain percentage, top model signals.'],['Credit Dashboard','KPI cards, filtered credit records, approval distribution, income and risk analysis.'],['Fraud Dashboard','Fraud transaction summaries, fraud type distribution, risk breakdown, filtered transaction records.']])
h(1,'4.3 Data Reports')
tbl(['Report','Data Included'],[['Credit Approval Report','Approval categories, income bands, risk profiles, applicant attributes.'],['Credit Amount Report','Maximum credit amount and credit band related output.'],['Fraud Detection Report','Transaction details, anomaly features, risk score, fraud verdict.'],['Prediction Log Report','Employee ID, module name, input payload, prediction label, score, timestamp.'],['Model Evaluation Reports','Classification report, confusion matrix, metrics JSON, feature columns.']])
h(1,'4.4 Sample Program Code')
code('''def predict_enhanced_approved_flag(input_payload: dict) -> dict:\n    artifact = load_artifact(ENHANCED_MODEL_PATH)\n    model = artifact["model"]\n    label_encoder = artifact["label_encoder"]\n    feature_columns = artifact["feature_columns"]\n\n    frame = pd.DataFrame([input_payload])\n    frame = frame.reindex(columns=feature_columns)\n\n    probabilities = model.predict_proba(frame)[0]\n    probabilities = probabilities / probabilities.sum()\n    predicted_index = int(probabilities.argmax())\n    predicted_label = label_encoder.inverse_transform([predicted_index])[0]\n\n    return {\n        "predicted_approved_flag": predicted_label,\n        "confidence": float(probabilities[predicted_index]),\n    }''')
h(1,'4.5 Limitations')
tbl(['No.','Limitation'],[['1','Model quality depends on training data quality, freshness, and representativeness.'],['2','Streamlit Community Cloud does not provide durable local database persistence after restarts; external DATABASE_URL is recommended.'],['3','Large joblib artifacts can increase startup time and deployment size.'],['4','ML predictions support decision-making but should not replace final human or policy review.'],['5','Dependency versions must remain compatible with saved model artifacts.'],['6','Current employee management is limited to seeded/demo employee unless an admin module is expanded.']])
h(1,'4.6 Test Cases')
tbl(['Test Case ID','Scenario','Input','Expected Result'],[['TC-01','Valid login','ANL001 with correct password','Dashboard is shown.'],['TC-02','Invalid login','Wrong password','Login error is displayed.'],['TC-03','Credit prediction','Valid applicant and bureau values','Approval category, confidence, amount, and probabilities are shown.'],['TC-04','Fraud prediction','Valid transaction values','Fraud probability, risk badge, verdict, and signals are shown.'],['TC-05','Prediction log','Authenticated user submits prediction','Row is inserted into prediction_logs.'],['TC-06','Dashboard filter','Select approval/fraud filters','Charts and tables update according to filters.'],['TC-07','Missing model file','Model artifact unavailable','Informative message is shown instead of app crash.'],['TC-08','Logout','Click Logout','Session clears and login page appears.']])

# DOCX writer with images
styles='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:sz w:val="22"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="36"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:i/><w:sz w:val="24"/></w:rPr></w:style><w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="30"/></w:rPr></w:style></w:styles>'''

def para(text='',style=None):
    ppr=f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    return f'<w:p>{ppr}<w:r><w:t xml:space="preserve">{escape(str(text))}</w:t></w:r></w:p>'

def table_xml(headers,rows):
    def cell(t,b=False):
        br='<w:b/>' if b else ''
        return f'<w:tc><w:tcPr><w:tcW w:w="2800" w:type="dxa"/></w:tcPr><w:p><w:r><w:rPr>{br}</w:rPr><w:t xml:space="preserve">{escape(str(t))}</w:t></w:r></w:p></w:tc>'
    out=['<w:tbl><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/><w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/><w:insideH w:val="single" w:sz="4"/><w:insideV w:val="single" w:sz="4"/></w:tblBorders></w:tblPr>']
    out.append('<w:tr>'+''.join(cell(x,True) for x in headers)+'</w:tr>')
    for r in rows: out.append('<w:tr>'+''.join(cell(x) for x in r)+'</w:tr>')
    out.append('</w:tbl>')
    return ''.join(out)

def code_xml(text):
    return ''.join(f'<w:p><w:r><w:rPr><w:rFonts w:ascii="Consolas" w:hAnsi="Consolas"/><w:sz w:val="18"/></w:rPr><w:t xml:space="preserve">{escape(line)}</w:t></w:r></w:p>' for line in text.splitlines())

image_rels=[]; media=[]
def img_xml(path,w_px,h_px):
    rid=f'rId{len(image_rels)+2}'
    name=f'image{len(image_rels)+1}.png'
    image_rels.append((rid,name))
    media.append((name,Path(path).read_bytes()))
    cx=int(w_px*9525); cy=int(h_px*9525)
    return f'''<w:p><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:docPr id="{len(image_rels)}" name="Picture {len(image_rels)}"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="{name}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'''

body=[]
for block in blocks:
    kind=block[0]
    if kind=='p': body.append(para(block[1],block[2]))
    elif kind=='h': body.append(para(block[1],'Heading1'))
    elif kind=='table': body.append(table_xml(block[1],block[2]))
    elif kind=='code': body.append(code_xml(block[1]))
    elif kind=='img': body.append(img_xml(block[1],block[2],block[3]))

document='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>'+''.join(body)+'<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:right="900" w:bottom="900" w:left="900"/></w:sectPr></w:body></w:document>'
content='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
rels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
docrels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' + ''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>' for rid,name in image_rels) + '</Relationships>'
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',content); z.writestr('_rels/.rels',rels); z.writestr('word/_rels/document.xml.rels',docrels); z.writestr('word/document.xml',document); z.writestr('word/styles.xml',styles)
    for name,data in media: z.writestr('word/media/'+name,data)
print(str(OUT))
