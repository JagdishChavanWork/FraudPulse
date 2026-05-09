from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from html import escape
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(r'E:\FraudPulse')
DOCS = ROOT / 'docs'
ASSETS = DOCS / 'finintel_current_project_assets'
OUT = DOCS / 'FinIntel_Current_Project_Input_Output_Database_Design.docx'
SCHEMA = (ROOT / 'database' / 'schema.sql').read_text(encoding='utf-8')
ASSETS.mkdir(parents=True, exist_ok=True)

try:
    FONT = ImageFont.truetype('arial.ttf', 17)
    FONT_B = ImageFont.truetype('arialbd.ttf', 18)
    FONT_H = ImageFont.truetype('arialbd.ttf', 28)
    FONT_M = ImageFont.truetype('arialbd.ttf', 22)
    FONT_S = ImageFont.truetype('arial.ttf', 14)
except Exception:
    FONT = FONT_B = FONT_H = FONT_M = FONT_S = ImageFont.load_default()

INK = '#173244'
BLUE = '#315f7d'
GREEN = '#2e7d32'
RED = '#9f3434'
AMBER = '#8a5b00'
BG = '#f6f9fb'

def wrap(text, width):
    words = str(text).split()
    lines, line = [], ''
    for word in words:
        test = (line + ' ' + word).strip()
        if len(test) <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def text(draw, xy, value, font=FONT, fill=INK):
    draw.text(xy, str(value), font=font, fill=fill)


def title(draw, value, width):
    bbox = draw.textbbox((0, 0), value, font=FONT_H)
    draw.text(((width - (bbox[2]-bbox[0]))/2, 24), value, font=FONT_H, fill=INK)


def card(draw, xy, heading, lines=None, fill='white', outline=BLUE):
    x1,y1,x2,y2 = xy
    draw.rounded_rectangle(xy, radius=12, fill=fill, outline=outline, width=2)
    draw.rectangle((x1, y1, x2, y1+44), fill=outline)
    bbox = draw.textbbox((0,0), heading, font=FONT_B)
    draw.text((x1 + 14, y1 + 12), heading, font=FONT_B, fill='white')
    y = y1 + 58
    for line in (lines or []):
        for part in wrap(line, max(24, int((x2-x1)/9))):
            draw.text((x1+16, y), part, font=FONT_S, fill=INK)
            y += 21
        y += 3


def arrow(draw, start, end, fill='#37474f'):
    import math
    draw.line([start, end], fill=fill, width=3)
    sx,sy = start; ex,ey = end
    ang = math.atan2(ey-sy, ex-sx)
    l = 12
    pts = [(ex,ey),(ex-l*math.cos(ang-.45),ey-l*math.sin(ang-.45)),(ex-l*math.cos(ang+.45),ey-l*math.sin(ang+.45))]
    draw.polygon(pts, fill=fill)


def input_box(draw, xy, label, value=''):
    x1,y1,x2,y2 = xy
    text(draw, (x1, y1-22), label, FONT_S, '#4d6575')
    draw.rounded_rectangle(xy, radius=8, fill='white', outline='#9fb4c3', width=1)
    if value:
        text(draw, (x1+12, y1+11), value, FONT, '#263238')


def button(draw, xy, label, fill=BLUE):
    draw.rounded_rectangle(xy, radius=8, fill=fill, outline=fill, width=1)
    bbox = draw.textbbox((0,0), label, font=FONT_B)
    x1,y1,x2,y2=xy
    draw.text((x1+(x2-x1-(bbox[2]-bbox[0]))/2, y1+(y2-y1-(bbox[3]-bbox[1]))/2-2), label, font=FONT_B, fill='white')


def metric(draw, xy, label, value, color=BLUE):
    x1,y1,x2,y2=xy
    draw.rounded_rectangle(xy, radius=10, fill='white', outline='#d4e0e8', width=1)
    text(draw, (x1+14,y1+12), label, FONT_S, '#647987')
    text(draw, (x1+14,y1+40), value, FONT_M, color)


def save_login(path):
    W,H=1200,720; im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im); title(d,'FinIntel - Login Input Screen',W)
    card(d,(370,145,830,590),'Employee Login',['Secure employee authentication using bcrypt password verification and Streamlit session state.'], '#ffffff', BLUE)
    input_box(d,(430,285,770,330),'Employee ID','ANL001')
    input_box(d,(430,385,770,430),'Password','********')
    button(d,(430,485,770,535),'Login')
    im.save(path)


def save_credit_input(path):
    W,H=1500,1000; im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im); title(d,'FinIntel - Credit Risk Prediction Input Screen',W)
    card(d,(60,105,1440,930),'Credit Risk Prediction Form',[], '#fff', BLUE)
    sections=[('Applicant Profile',80,175),('Bureau & Tradeline Summary',80,390),('Advanced Bureau Indicators',80,610)]
    for name,x,y in sections: text(d,(x,y),name,FONT_M,INK)
    fields1=[('Applicant age','35'),('Net monthly income','45000'),('Employer tenure','36'),('Education','GRADUATE'),('Gender','M'),('Marital status','Single')]
    x,y=80,225
    for i,(lab,val) in enumerate(fields1): input_box(d,(x+(i%3)*450,y+(i//3)*95,x+(i%3)*450+350,y+(i//3)*95+45),lab,val)
    fields2=[('Total tradelines','8'),('Active tradelines','4'),('Opened L6M','1'),('Secured TL','3'),('Unsecured TL','4'),('Credit Card TL','1'),('Personal Loan TL','1'),('Home Loan TL','0')]
    x,y=80,440
    for i,(lab,val) in enumerate(fields2): input_box(d,(x+(i%4)*340,y+(i//4)*85,x+(i%4)*340+260,y+(i//4)*85+45),lab,val)
    fields3=[('Missed payments','0'),('Recent delinquency','0'),('Max delinquency','0'),('Enquiries L3M','1'),('CC enquiries L12M','0'),('PL enquiries L12M','0'),('First product enquiry','others'),('Last product enquiry','others')]
    x,y=80,660
    for i,(lab,val) in enumerate(fields3): input_box(d,(x+(i%4)*340,y+(i//4)*85,x+(i%4)*340+260,y+(i//4)*85+45),lab,val)
    button(d,(1100,830,1390,885),'Analyze Credit Profile',GREEN)
    im.save(path)


def save_credit_output(path):
    W,H=1200,780; im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im); title(d,'FinIntel - Credit Risk Prediction Output Screen',W)
    card(d,(70,120,1130,700),'AI Recommendation - Credit Risk',[], '#fff', BLUE)
    metric(d,(110,190,430,285),'Predicted approval category','P2',GREEN)
    metric(d,(455,190,775,285),'Model confidence','92.1%',BLUE)
    metric(d,(800,190,1090,285),'Maximum credit amount','Rs. 2,40,000',AMBER)
    card(d,(110,340,1090,625),'Class Probabilities',['P1 : 2.4%','P2 : 92.1%','P3 : 4.6%','P4 : 0.9%','Prediction is logged in prediction_logs with employee ID, module name, input payload, label, score, and timestamp.'], '#ffffff', GREEN)
    im.save(path)


def save_fraud_input(path):
    W,H=1500,1000; im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im); title(d,'FinIntel - Fraud Detection Prediction Input Screen',W)
    card(d,(60,105,1440,930),'Fraud Detection Form',[], '#fff', RED)
    text(d,(80,175),'Customer Profile',FONT_M,INK)
    fields=[('Customer age','35'),('Account type','Savings'),('City tier','2'),('Account tenure days','1800'),('Account balance','75000')]
    for i,(lab,val) in enumerate(fields): input_box(d,(80+(i%3)*450,225+(i//3)*90,80+(i%3)*450+350,270+(i//3)*90),lab,val)
    text(d,(80,405),'Normal Spending Baseline',FONT_M,INK)
    fields=[('Avg monthly spend','25000'),('Avg txn amount','2500'),('Avg txns per day','2'),('Usual txn hour','11')]
    for i,(lab,val) in enumerate(fields): input_box(d,(80+i*340,455,80+i*340+260,500),lab,val)
    text(d,(80,585),'Reported Transaction',FONT_M,INK)
    fields=[('Transaction type','UPI'),('Transaction amount','15000'),('Transaction hour','23'),('Day of week','Sunday'),('Velocity 24H','4'),('Days since last txn','1')]
    for i,(lab,val) in enumerate(fields): input_box(d,(80+(i%3)*450,635+(i//3)*90,80+(i%3)*450+350,680+(i//3)*90),lab,val)
    button(d,(1110,830,1390,885),'Verify Transaction',RED)
    im.save(path)


def save_fraud_output(path):
    W,H=1200,780; im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im); title(d,'FinIntel - Fraud Detection Output Screen',W)
    card(d,(70,120,1130,700),'Verification Result - Fraud Detection',[], '#fff', RED)
    metric(d,(110,190,430,285),'Fraud probability','84.5%',RED)
    metric(d,(455,190,775,285),'Decision threshold','50%',BLUE)
    metric(d,(800,190,1090,285),'Risk level','HIGH',RED)
    card(d,(110,335,1090,625),'Final Verdict',['FRAUD VERIFIED. Escalate immediately and restrict the transaction.','Amount vs Avg: 6.00x','Balance Drain: 20.0%','Top model signals: velocity_24hr, balance_drain_pct, hour_anomaly, new_txn_type_flag'], '#ffffff', RED)
    im.save(path)


def save_dashboard_output(path):
    W,H=1300,850; im=Image.new('RGB',(W,H),BG); d=ImageDraw.Draw(im); title(d,'FinIntel - Management Insights Output Screen',W)
    card(d,(55,110,1245,760),'Management Insights Dashboard',[], '#fff', BLUE)
    metric(d,(95,185,355,270),'Total Records','42,064',BLUE)
    metric(d,(385,185,645,270),'Approval P1/P2','68%',GREEN)
    metric(d,(675,185,935,270),'Fraud Cases','High Risk',RED)
    metric(d,(965,185,1205,270),'Avg Income','Rs. 45,000',AMBER)
    card(d,(95,330,580,680),'Credit Risk Dashboard Output',['Approval distribution chart','Income bucket analysis','Risk profile distribution','Filtered credit records table'], '#ffffff', GREEN)
    card(d,(720,330,1205,680),'Fraud Dashboard Output',['Fraud type distribution','Transaction risk bands','Suspicious transaction records','Risk score based summaries'], '#ffffff', RED)
    im.save(path)


def save_er(path):
    W,H=1700,1120; im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im); title(d,'FinIntel Current Database ER Diagram',W)
    def tcard(xy, name, fields, color): card(d,xy,name,fields,'#ffffff',color)
    tcard((70,150,455,380),'employees',['PK id','UK employee_id','employee_name','employee_password_hash','is_active','created_at, updated_at'],AMBER)
    tcard((650,440,1050,735),'prediction_logs',['PK id','FK employee_id','module_name','input_payload','prediction_label','prediction_score','created_at'],BLUE)
    tcard((70,690,455,960),'credit_risk_data',['PK id','age, education, gender','net_monthly_income','approved_flag','credit_band','max_credit_amount','risk_profile'],GREEN)
    tcard((1235,130,1640,435),'credit_risk_dashboard_enhanced',['PK id','tradeline features','delinquency features','enquiry features','approved_flag','income_bucket','risk_profile'],GREEN)
    tcard((1235,690,1640,980),'fraud_detection_data',['PK id','UK transaction_id','txn_type, txn_amount','anomaly features','risk_score','risk_band','is_fraud'],RED)
    arrow(d,(455,265),(650,545)); text(d,(500,360),'employee creates prediction logs',FONT,INK)
    arrow(d,(455,825),(650,640)); text(d,(500,760),'credit prediction audit',FONT,INK)
    arrow(d,(1235,280),(1050,545)); text(d,(1055,365),'enhanced credit payload source',FONT,INK)
    arrow(d,(1235,825),(1050,640)); text(d,(1060,760),'fraud prediction audit',FONT,INK)
    im.save(path)

asset_paths={
    'login': ASSETS/'01_login_input.png',
    'credit_input': ASSETS/'02_credit_risk_input.png',
    'credit_output': ASSETS/'03_credit_risk_output.png',
    'fraud_input': ASSETS/'04_fraud_detection_input.png',
    'fraud_output': ASSETS/'05_fraud_detection_output.png',
    'dashboard_output': ASSETS/'06_management_dashboard_output.png',
    'er': ASSETS/'07_current_database_er_diagram.png',
}
save_login(asset_paths['login']); save_credit_input(asset_paths['credit_input']); save_credit_output(asset_paths['credit_output'])
save_fraud_input(asset_paths['fraud_input']); save_fraud_output(asset_paths['fraud_output']); save_dashboard_output(asset_paths['dashboard_output']); save_er(asset_paths['er'])

blocks=[]
def p(t='',style=None): blocks.append(('p',t,style))
def h(t): blocks.append(('h',t,None))
def tbl(headers,rows): blocks.append(('table',headers,rows))
def img(path,w,h): blocks.append(('img',str(path),w,h))
def code(t): blocks.append(('code',t,None))

p('FinIntel - Current Project Input / Output Screens and Database Design','Title')
p('This document is generated from the current FinIntel Streamlit modules, prediction forms, SQLAlchemy database models, and schema.sql.','Subtitle')

h('1. Input Screens')
p('1.1 Login Input Screen','Heading2'); img(asset_paths['login'],610,365)
p('The employee enters Employee ID and Password. The authentication module validates the active employee record and bcrypt password hash.')
p('1.2 Credit Risk Prediction Input Screen','Heading2'); img(asset_paths['credit_input'],650,430)
p('This screen represents the current credit_risk.py form: applicant profile, bureau/tradeline summary, advanced bureau indicators, product enquiries, and loan flags.')
p('1.3 Fraud Detection Prediction Input Screen','Heading2'); img(asset_paths['fraud_input'],650,430)
p('This screen represents the current fraud_detection.py form: customer profile, baseline spending, reported transaction, velocity, anomaly flags, and verification submission.')
tbl(['Input Area','Current Project Inputs'],[
    ['Login','Employee ID, password'],
    ['Credit Applicant Profile','Applicant age, net monthly income, current employer tenure, education, gender, marital status'],
    ['Credit Bureau & Tradeline','Total tradelines, active tradelines, opened L6M, secured/unsecured TL, CC/PL/Home TL'],
    ['Advanced Credit Indicators','Missed payments, delinquency levels, enquiries, open/closed tradeline percentages, product enquiry values, loan flags'],
    ['Fraud Customer Profile','Customer age, account type, city tier, tenure days, account balance'],
    ['Fraud Transaction Profile','Transaction type, amount, hour, day of week, velocity 24H, days since last transaction, anomaly flags'],
])

h('2. Output Screens')
p('2.1 Management Insights Output Screen','Heading2'); img(asset_paths['dashboard_output'],640,410)
p('This screen represents the current management_insights.py module with Credit Risk Dashboard and Fraud Dashboard tabs.')
p('2.2 Credit Risk Prediction Output Screen','Heading2'); img(asset_paths['credit_output'],610,395)
p('The current credit module displays predicted approval category, model confidence, maximum credit amount, and class probabilities.')
p('2.3 Fraud Detection Prediction Output Screen','Heading2'); img(asset_paths['fraud_output'],610,395)
p('The current fraud module displays fraud probability, decision threshold, risk level, final verdict, derived signals, and top model signals.')
tbl(['Output Area','Current Project Outputs'],[
    ['Management Insights','Credit KPIs, fraud KPIs, charts, risk summaries, filtered records'],
    ['Credit Risk Prediction','Approval category, confidence percentage, maximum credit amount, class probabilities'],
    ['Fraud Detection Prediction','Fraud probability, threshold, risk level, final verdict, amount-to-average ratio, balance drain, top model signals'],
    ['Prediction Logging','Employee ID, module name, serialized payload, predicted label, score, timestamp'],
])

h('3. Database Design - Current ER Diagram')
img(asset_paths['er'],650,430)
p('The diagram shows the current database design used by FinIntel. The employees table creates prediction_logs. Credit and fraud modules save prediction audit records after model execution.')

h('4. Database Tables')
tbl(['Table Name','Primary Key','Important Columns','Purpose'],[
    ['employees','id','employee_id, employee_name, employee_password_hash, is_active, created_at, updated_at','Stores employee login and account status.'],
    ['credit_risk_data','id','age, education, gender, marital_status, net_monthly_income, approved_flag, credit_band, max_credit_amount','Stores summarized credit risk records and outcomes.'],
    ['credit_risk_dashboard_enhanced','id','tradeline features, delinquency features, enquiry features, approved_flag, income_bucket, risk_profile','Stores enhanced credit dashboard and model feature records.'],
    ['fraud_detection_data','id','transaction_id, txn_type, txn_amount, anomaly fields, risk_score, risk_band, is_fraud','Stores transaction records and fraud risk output.'],
    ['prediction_logs','id','employee_id, module_name, input_payload, prediction_label, prediction_score, created_at','Stores prediction audit history for credit and fraud modules.'],
])

h('5. Current Database Schema')
code(SCHEMA)

h('6. Data Dictionary')
tbl(['Field','Type','Table','Description'],[
    ['employee_id','String(30)','employees, prediction_logs','Unique employee identifier and prediction owner reference.'],
    ['employee_password_hash','String(255)','employees','bcrypt hashed password.'],
    ['net_monthly_income','Float','credit tables','Applicant monthly income.'],
    ['approved_flag','String(20)','credit tables','Credit approval class such as P1, P2, P3, P4.'],
    ['credit_band','String(40)','credit_risk_data','Assigned credit band.'],
    ['max_credit_amount','Float','credit_risk_data','Estimated maximum credit amount.'],
    ['transaction_id','String(80)','fraud_detection_data','Unique transaction or case identifier.'],
    ['txn_type','String(40)','fraud_detection_data','Transaction mode/type.'],
    ['txn_amount','Float','fraud_detection_data','Transaction amount.'],
    ['amount_to_avg_ratio','Float','fraud_detection_data','Transaction amount compared with normal average.'],
    ['balance_drain_pct','Float','fraud_detection_data','Percentage of account balance used by transaction.'],
    ['risk_score','Float','fraud_detection_data','Fraud risk score.'],
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
    rid=f'rId{len(image_rels)+2}'; name=f'image{len(image_rels)+1}.png'
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
content='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="png" ContentType="image/png"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'
rels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
docrels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>' + ''.join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/{name}"/>' for rid,name in image_rels) + '</Relationships>'
with ZipFile(OUT,'w',ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',content); z.writestr('_rels/.rels',rels); z.writestr('word/_rels/document.xml.rels',docrels); z.writestr('word/document.xml',document); z.writestr('word/styles.xml',styles)
    for name,data in media: z.writestr('word/media/'+name,data)
print(OUT)
