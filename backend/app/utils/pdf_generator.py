
"""
PDF Generator Utils (app/utils/pdf_generator.py)
"""
from typing import Dict, Any, Optional, BinaryIO
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch

    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("ReportLab not available. PDF generation will be limited.")


class PDFGenerator:
    """PDF generation utilities"""

    def __init__(self):
        self.available = REPORTLAB_AVAILABLE

    def generate_paper_pdf(
            self,
            paper_data: Dict[str, Any],
            include_sections: bool = True,
            include_metadata: bool = True
    ) -> bytes:
        """Generate PDF from paper data"""

        if not self.available:
            raise Exception("PDF generation not available. Install reportlab: pip install reportlab")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph(paper_data.get('title', 'Untitled Paper'), title_style))
        story.append(Spacer(1, 12))

        # Authors
        if paper_data.get('co_authors'):
            authors = ', '.join(paper_data['co_authors'])
            story.append(Paragraph(f"<b>Authors:</b> {authors}", styles['Normal']))
            story.append(Spacer(1, 12))

        # Metadata
        if include_metadata:
            metadata_items = [
                f"<b>Research Area:</b> {paper_data.get('research_area', 'N/A')}",
                f"<b>Status:</b> {paper_data.get('status', 'draft').title()}",
                f"<b>Progress:</b> {paper_data.get('progress', 0)}%",
                f"<b>Word Count:</b> {paper_data.get('current_word_count', 0)} / {paper_data.get('target_word_count', 0)}",
                f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ]

            for item in metadata_items:
                story.append(Paragraph(item, styles['Normal']))

            story.append(Spacer(1, 20))

        # Abstract
        if paper_data.get('abstract'):
            story.append(Paragraph("<b>Abstract</b>", styles['Heading2']))
            story.append(Paragraph(paper_data['abstract'], styles['Normal']))
            story.append(Spacer(1, 20))

        # Sections
        if include_sections and paper_data.get('sections'):
            for section in sorted(paper_data['sections'], key=lambda x: x.get('order', 0)):
                # Section title
                story.append(Paragraph(section.get('title', 'Untitled Section'), styles['Heading2']))
                story.append(Spacer(1, 12))

                # Section content
                content = section.get('content', 'No content available.')
                story.append(Paragraph(content, styles['Normal']))
                story.append(Spacer(1, 20))

        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_analytics_report_pdf(self, analytics_data: Dict[str, Any]) -> bytes:
        """Generate analytics report as PDF"""

        if not self.available:
            raise Exception("PDF generation not available. Install reportlab: pip install reportlab")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("Research Analytics Report", styles['Title']))
        story.append(Spacer(1, 20))

        # Summary
        story.append(Paragraph("Summary", styles['Heading1']))
        summary_items = [
            f"Total Papers: {analytics_data.get('total_papers', 0)}",
            f"Published Papers: {analytics_data.get('published_papers', 0)}",
            f"Total Words: {analytics_data.get('total_words', 0):,}",
            f"Average Progress: {analytics_data.get('avg_progress', 0):.1f}%"
        ]

        for item in summary_items:
            story.append(Paragraph(item, styles['Normal']))

        story.append(Spacer(1, 20))

        # Research Areas
        if analytics_data.get('research_areas'):
            story.append(Paragraph("Research Areas", styles['Heading1']))
            for area, count in analytics_data['research_areas'].items():
                story.append(Paragraph(f"• {area}: {count} papers", styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

