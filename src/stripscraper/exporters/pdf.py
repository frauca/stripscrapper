"""PDF Exporter - Exporta classificacions a PDF."""

from datetime import datetime
from typing import List
from pathlib import Path

from loguru import logger
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from stripscraper.models import GlobalClassification


class PDFExporter:

    def export(self, classifications: List[GlobalClassification], filepath: Path):
        for classification in classifications:
            self._export_classification(classification, filepath)

    def _export_classification(self, classification: GlobalClassification, filepath: Path):
        file_name = f"{classification.category}-{datetime.today().strftime('%Y-%m-%d')}.pdf"
        pdf_file = Path(filepath / file_name)
        pdf_file.unlink(missing_ok=True)
        pdf_file.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"Exporting {pdf_file}")

        doc = SimpleDocTemplate(str(pdf_file), pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        story = []

        title = Paragraph(f"<b>{classification.category}</b>", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 0.5*cm))

        data = [[
            'Pos',
            'Equip',
            'Pond',
            'Punts',
            'Grup',
            'Pos Grup',
            'Part',
            'Vict',
            'Derr',
            'Sets+',
            'Sets-',
            'Dif Sets',
            'Punts+',
            'Punts-',
            'Dif Punts'
        ]]

        for i, team in enumerate(classification.teams, start=1):
            data.append([
                str(i),
                team.stats.name,
                f"{team.stats.points_percentage:.0f}",
                str(team.stats.total_points),
                team.group,
                str(team.stats.position),
                str(team.stats.matches_played),
                str(team.stats.matches_won),
                str(team.stats.matches_lost),
                str(team.stats.sets_for),
                str(team.stats.sets_against),
                str(team.stats.sets_difference),
                str(team.stats.points_for),
                str(team.stats.points_against),
                str(team.stats.points_difference)
            ])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
        ]))

        story.append(table)
        doc.build(story)