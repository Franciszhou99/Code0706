from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, SimpleDocTemplate, Paragraph, Image, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors, styles
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Drawing
from reportlab.lib.units import cm, inch
from reportlab.pdfgen import canvas


from reportlab.pdfgen.canvas import Canvas


pdfmetrics.registerFont(TTFont('TNR', '../charge_web_app/web/Font/times new roman.ttf'))
# pdfmetrics.registerFont(TTFont('TNRB', 'timesbd.ttf'))

class Graphs:
    @staticmethod
    def draw_title(title: str):
        style = getSampleStyleSheet()
        ct = style['Heading1']
        ct.fontName = 'TNR'
        ct.fontSize = 26
        ct.leading = 50
        ct.textColor = colors.black
        ct.alignment = 1
        ct.bold = True
        return Paragraph(title, ct)

    @staticmethod
    def draw_little_title(title:str,doc):
        style = getSampleStyleSheet()
        ct = style['Normal']
        ct.fontName = 'TNR'
        ct.fontSize = 18
        ct.leading = 30
        ct.textColor = colors.black
        return Paragraph(title, ct)

    @staticmethod
    def draw_text(text:str):
        style = getSampleStyleSheet()
        ct = style['Normal']
        ct.fontName = 'TNR'
        ct.fontSize = 12
        ct.wordWrap = 'CJK'
        ct.alignment = 0
        ct.firstLineIndent = 32
        ct.leading = 25
        return Paragraph(text,ct)

    @staticmethod
    def draw_table(table_data,doc):
        style = getSampleStyleSheet()
        page_width, _ = A4
        max_widths = [max([len(str(row[i])) for row in table_data]) for i in range(len(table_data[0]))]
        col_widths = [width * 10 for width in max_widths]  # 10 为每个字符的宽度
        table_width = sum(col_widths)
        left_margin = 40  # 左侧留白宽度
        right_margin = 40 # 右侧留白宽度
        total_width = page_width - left_margin - right_margin
        if table_width > total_width:
            scale = total_width / table_width
            col_widths = [int(width * scale) for width in col_widths]

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'TNR'),  # 字体
            ('FONTSIZE', (0, 0), (-1, 0), 9),  # 第一行的字体大小
            ('FONTSIZE', (0, 1), (-1, -1), 8),  # 第二行到最后一行的字体大小
            ('BACKGROUND', (0, 0), (-1, 0), '#d5dae6'),  # 设置第一行背景颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 第一行水平居中
            ('ALIGN', (0, 1), (-1, -1), 'CENTER'),  # 第二行到最后一行左右左对齐
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 所有表格上下居中对齐
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为grey色，线宽为0.5
        ]))
        table.wrapOn(doc, 500, 400)
        table.drawOn(doc, 50, 585)
        doc.saveState()

    @staticmethod
    def draw_column_table(column1:list,column2:list,column3:list,doc):
        table_data = [[row1,row2,row3] for row1,row2,row3 in zip(column1,column2,column3)]
        style = getSampleStyleSheet()
        custom_style = ParagraphStyle('CustomStyle', parent=style['Normal'])
        for i, row in enumerate(table_data):
            for j, cell in enumerate(row):
                table_data[i][j] = Paragraph(cell, custom_style)
        # print(table_data)
        page_width, _ = A4
        left_margin = 40  # 左侧留白宽度
        right_margin = 40 # 右侧留白宽度
        table_width = page_width - left_margin - right_margin
        num_cols = len(table_data[0])
        col_width = table_width / num_cols
        table1 = Table(table_data,colWidths=col_width)

        table1.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # 第一行的字体大小
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # 第二行到最后一行的字体大小
            # ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (0, 0), '#d5dae6'),
            ('BACKGROUND', (-1, 0), (-1, 0), '#d5dae6'),
        ]))
        table1.wrapOn(doc,500,400)
        table1.drawOn(doc,50,640)
        doc.saveState()

    @staticmethod
    def draw_chart(self,chart_data:list, ax:list, items: list):
        drawing = Drawing(500,250)
        chart = LinePlot()
        chart.data = chart_data
        n = 0
        for i in chart_data:
            chart.lines[n].symbol = makeMarker('circle')
            n=n+1
        chart.x = 45
        chart.y = 45
        chart.height = 200
        chart.width = 350
        chart.strokeColor = colors.black

        chart.lineLabelFormat = '%2.0f'

        leg = Legend()
        leg.fontName = 'TNR'
        leg.alignment = 'right'
        leg.boxAnchor = 'ne'
        leg.x = 475
        leg.y = 240
        leg.dxTextSpace = 10
        leg.columnMaximum = 3
        leg.colorNamePairs = items
        drawing.add(leg)
        drawing.add(chart)
        return drawing

    @staticmethod
    def draw_img(path,doc):
        img = Image(path)
        img.drawWidth = 5*cm
        img.drawHeight = 2*cm
        img.hAlign = 'LEFT'

        y = doc._pagesize[1] - img.drawHeight - 30
        img.drawOn(doc,50,y)
        doc.saveState()

    def footer(self,doc):
        style = getSampleStyleSheet()
        custom_style= ParagraphStyle(name = 'Customestyle',
                                     parent=['Normal'],
                                     fontSize = 12,
                                     textColor='blue',
                                     alignment = 1,
                                     )
        doc.saveState()
        page_num = doc.getPageNumber()
        bottom_margin = 0.5 * inch
        left_margin = 0.5 * inch
        content = Paragraph(f"Page {page_num} ",custom_style)
        w,h = content.wrap(doc._pagesize[0], bottom_margin)
        content.drawOn(doc,left_margin, h)
        doc.restoreState()

    def header(self, doc):
        style = getSampleStyleSheet()
        custom_style = ParagraphStyle(name='Customestyle',
                                      parent=['Normal'],
                                      fontSize=12,
                                      textColor='blue',
                                      alignment=1,
                                      )
        doc.saveState()
        top_margin = 0.5 * inch
        left_margin = 0.5 * inch
        header_content = Paragraph("页眉", custom_style)
        w,h = header_content.wrap(doc._pagesize[0],top_margin)
        header_content.drawOn(doc , left_margin, h + top_margin)
        doc.restoreState()














