from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.pagesizes import A4, portrait
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import mm,cm
from reportlab.lib import colors
from io import BytesIO
def makePDF(name,data,total):
	pdf_buffer = BytesIO()

	pdfFile = canvas.Canvas(pdf_buffer,bottomup=False)
	pdfFile.saveState()
	
	# フォントサイズ定義（この場合は24）
	font_size = 24
	font_name = 'HeiseiKakuGo-W5'
	
	# フォント登録
	pdfmetrics.registerFont(UnicodeCIDFont(font_name))
	
	pdfFile.setFont(font_name, font_size)
	
	pdfFile.setAuthor('福本伸子')
	pdfFile.setTitle('name')
	 
	# A4
	pdfFile.setPageSize((21.0*cm, 29.7*cm))
	
	#合計金額の表 
	total_list =[["合計金額:","{:,}".format(total)+"円"]]
	total_table = Table(total_list, colWidths=(20*mm, 43*mm), rowHeights=(8*mm))
	
	total_table.setStyle(TableStyle([
		('FONT', (0, 0), (0, 0), font_name, 9),
		('FONT', (1, 0), (1, 0), font_name, 12),
		('BOX', (0, 0), (-1, -1), 1, colors.black),
		('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
		("BOTTOMPADDING", (0, 0), (-1, -1), 12),
	]))
	
	total_table.wrapOn(pdfFile, 14*mm, 65*mm)
	total_table.drawOn(pdfFile, 14*mm, 65*mm)
	
	#数値はカンマを付ける
	data = list(map(lambda x:x[0:2]+["{:,}".format(x[2])]+["{:,}".format(x[3])], data))
	data.insert(0,["品名","数量","単価","金額"])
	
	data = data[::-1]
	data_table = Table(data, colWidths=(103*mm, 27*mm,21*mm,30*mm), rowHeights=(8*mm))
	
	
	
	data_table.setStyle(TableStyle([
		('FONT', (0, 0), (-1, -1), font_name, 12),
		('INNERGRID', (0, 0), (-1, -1), 1, colors.black),
		('BOX', (0, 0), (-1, -1), 1, colors.black),
		('ALIGN', (0, 0), (-1, -1), 'CENTER'),
		('ALIGN', (0, 0), (0, len(data)-2), 'LEFT'),
		("BOTTOMPADDING", (0, 0), (-1, -1), 12),
	]))
	
	data_table.wrapOn(pdfFile, 14*mm, 90*mm)
	data_table.drawOn(pdfFile, 14*mm, 90*mm)
	
	#発注書
	pdfFile.setFont('HeiseiKakuGo-W5', font_size)
	pdfFile.drawCentredString(10.5*cm,3*cm,"発 注 書")

	pdfFile.restoreState()
	pdfFile.save()
	return pdf_buffer
	
makePDF("test",[["テスト商品",1,1000,1000],["テスト商品",1,1000,1000],["テスト商品",1,1000,1000]],100000)