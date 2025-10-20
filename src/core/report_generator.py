"""
PDF Report Generator for forensic cases
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image as RLImage, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json

from ..database.case_repository import CaseRepository
from ..database.file_repository import FileRepository
from ..database.audit_repository import AuditRepository
from ..utils.logger import get_logger

class ReportGenerator:
    """Generate PDF reports for forensic cases"""
    
    def __init__(self):
        self.logger = get_logger()
        self.case_repo = CaseRepository()
        self.file_repo = FileRepository()
        self.audit_repo = AuditRepository()
    
    def generate_report(self, case_id: int, output_path: Path,
                       include_thumbnails: bool = True,
                       flagged_only: bool = False) -> bool:
        """
        Generate comprehensive case report

        Args:
            case_id: Case ID to generate report for
            output_path: Path to save PDF
            include_thumbnails: Whether to include image thumbnails
            flagged_only: If True, only include flagged evidence in report

        Returns:
            True if successful
        """
        try:
            report_type = "FLAGGED EVIDENCE ONLY" if flagged_only else "FULL CASE"
            self.logger.info(f"Generating {report_type} report for case {case_id}")

            # Get case data
            case = self.case_repo.get_case(case_id)
            if not case:
                raise ValueError(f"Case {case_id} not found")

            stats = self.case_repo.get_case_statistics(case_id)
            flagged_files = self.file_repo.get_files_by_case(case_id, flagged_only=True)

            # Get files based on report type
            if flagged_only:
                files = flagged_files
                if not files:
                    raise ValueError("No flagged evidence found in this case")
            else:
                files = self.file_repo.get_files_by_case(case_id)

            audit_logs = self.audit_repo.get_case_logs(case_id, limit=50)
            
            # Create PDF
            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=letter,
                rightMargin=0.75*inch,
                leftMargin=0.75*inch,
                topMargin=1*inch,
                bottomMargin=0.75*inch
            )
            
            # Build content
            story = []
            styles = self._get_styles()

            # Title page
            story.extend(self._build_title_page(case, styles, flagged_only))
            story.append(PageBreak())
            
            # Executive Summary
            story.extend(self._build_executive_summary(case, stats, styles))
            story.append(PageBreak())
            
            # Case Details
            story.extend(self._build_case_details(case, styles))
            story.append(Spacer(1, 0.3*inch))
            
            # Statistics
            story.extend(self._build_statistics(stats, styles))
            story.append(PageBreak())
            
            # Flagged Evidence
            if flagged_files:
                story.extend(self._build_flagged_section(flagged_files, styles))
                story.append(PageBreak())
            
            # All Files Summary
            story.extend(self._build_files_summary(files, styles))
            story.append(PageBreak())
            
            # AI Analysis Results
            story.extend(self._build_ai_analysis(files, styles))
            story.append(PageBreak())
            
            # Audit Trail
            story.extend(self._build_audit_trail(audit_logs, styles))
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_header_footer,
                     onLaterPages=self._add_header_footer)
            
            self.logger.info(f"Report generated: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return False
    
    def _get_styles(self):
        """Get custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0066FF'),
            spaceBefore=20,
            spaceAfter=12,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceBefore=10,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        styles.add(ParagraphStyle(
            name='Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))
        
        return styles
    
    def _build_title_page(self, case: Dict, styles, flagged_only: bool = False) -> List:
        """Build title page"""
        story = []

        # Logo/Title
        story.append(Spacer(1, 2*inch))
        story.append(Paragraph("FORENSTIQ AI TECHNOLOGIES", styles['CustomTitle']))
        story.append(Spacer(1, 0.1*inch))

        # Report type indicator
        if flagged_only:
            report_title = "⚠️ Flagged Evidence Report"
            report_subtitle = "(Flagged Items Only)"
        else:
            report_title = "Digital Forensic Analysis Report"
            report_subtitle = "(Complete Case Report)"

        story.append(Paragraph(report_title, styles['Heading2']))
        story.append(Paragraph(f"<i>{report_subtitle}</i>", styles['Normal']))
        
        story.append(Spacer(1, 1*inch))
        
        # Case info
        story.append(Paragraph(f"<b>Case Number:</b> {case['case_number']}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Case Name:</b> {case['case_name']}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Investigator:</b> {case.get('investigator_name', 'N/A')}", styles['Normal']))
        story.append(Spacer(1, 0.1*inch))
        story.append(Paragraph(f"<b>Agency:</b> {case.get('agency_name', 'N/A')}", styles['Normal']))
        
        story.append(Spacer(1, 1*inch))
        
        # Date
        report_date = datetime.now().strftime('%B %d, %Y')
        story.append(Paragraph(f"<b>Report Generated:</b> {report_date}", styles['Normal']))
        
        return story
    
    def _build_executive_summary(self, case: Dict, stats: Dict, styles) -> List:
        """Build executive summary"""
        story = []
        
        story.append(Paragraph("Executive Summary", styles['CustomHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        summary_text = f"""
        This report presents the findings from the digital forensic analysis of case 
        <b>{case['case_number']}</b> - {case['case_name']}. The analysis was conducted using 
        AI-powered tools to automatically process and categorize digital evidence.
        <br/><br/>
        <b>Key Findings:</b><br/>
        • Total files analyzed: {stats.get('total_files', 0)}<br/>
        • Files with AI analysis: {stats.get('processed_files', 0)}<br/>
        • Flagged items requiring attention: {stats.get('flagged_files', 0)}<br/>
        • Faces detected across evidence: {stats.get('total_faces', 0)}<br/>
        • Files containing text: {stats.get('files_with_faces', 0)}<br/>
        """
        
        story.append(Paragraph(summary_text, styles['Normal']))
        
        return story
    
    def _build_case_details(self, case: Dict, styles) -> List:
        """Build case details section"""
        story = []
        
        story.append(Paragraph("Case Information", styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Case details table
        data = [
            ['Case Number:', case['case_number']],
            ['Case Name:', case['case_name']],
            ['Investigator:', case.get('investigator_name', 'N/A')],
            ['Agency:', case.get('agency_name', 'N/A')],
            ['Incident Date:', case.get('incident_date', 'N/A')],
            ['Case Created:', case['created_date'].split('T')[0]],
            ['Status:', case['status'].upper()],
        ]
        
        table = Table(data, colWidths=[2*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F0F0')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(table)
        
        # Notes
        if case.get('notes'):
            story.append(Spacer(1, 0.2*inch))
            story.append(Paragraph("Case Notes:", styles['CustomSubHeading']))
            story.append(Paragraph(case['notes'], styles['Normal']))
        
        return story
    
    def _build_statistics(self, stats: Dict, styles) -> List:
        """Build statistics section"""
        story = []
        
        story.append(Paragraph("Analysis Statistics", styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Stats table
        data = [
            ['Metric', 'Count'],
            ['Total Files', str(stats.get('total_files', 0))],
            ['Processed Files', str(stats.get('processed_files', 0))],
            ['Flagged Files', str(stats.get('flagged_files', 0))],
            ['Files with Faces', str(stats.get('files_with_faces', 0))],
            ['Total Faces Detected', str(stats.get('total_faces', 0))],
            ['Unique Dates', str(stats.get('unique_dates', 0))],
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(table)
        
        return story
    
    def _build_flagged_section(self, flagged_files: List[Dict], styles) -> List:
        """Build flagged evidence section"""
        story = []
        
        story.append(Paragraph("⚠️ Flagged Evidence", styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        story.append(Paragraph(
            f"The following {len(flagged_files)} items have been flagged for attention:",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        for idx, file_data in enumerate(flagged_files[:20], 1):  # Limit to 20
            file_info = f"""
            <b>{idx}. {file_data['file_name']}</b><br/>
            """

            # Add relative path if available
            if file_data.get('file_relative_path'):
                file_info += f"Path: {file_data['file_relative_path']}<br/>"

            file_info += f"""
            Date: {file_data.get('date_taken', 'N/A')}<br/>
            Reason: {file_data.get('flag_reason', 'Manually flagged')}<br/>
            """

            # Add hash value
            if file_data.get('file_hash'):
                file_info += f"Hash (SHA-256): {file_data['file_hash'][:16]}...<br/>"

            if file_data.get('ai_tags'):
                try:
                    tags = json.loads(file_data['ai_tags'])
                    file_info += f"AI Tags: {', '.join(tags[:5])}<br/>"
                except:
                    pass

            story.append(Paragraph(file_info, styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
        
        if len(flagged_files) > 20:
            story.append(Paragraph(
                f"... and {len(flagged_files) - 20} more flagged items.",
                styles['Normal']
            ))
        
        return story
    
    def _build_files_summary(self, files: List[Dict], styles) -> List:
        """Build files summary table"""
        story = []

        story.append(Paragraph("Evidence Files Summary", styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))

        # Build table data
        data = [['#', 'Filename / Path', 'Hash (SHA-256)', 'Date', 'Type', 'Flag']]

        for idx, file_data in enumerate(files[:50], 1):  # Limit to 50
            # File name and relative path
            file_display = file_data['file_name'][:25] + '...' if len(file_data['file_name']) > 25 else file_data['file_name']
            if file_data.get('file_relative_path'):
                file_display += f"\n({file_data['file_relative_path'][:30]}...)" if len(file_data.get('file_relative_path', '')) > 30 else f"\n({file_data.get('file_relative_path', '')})"

            # Hash (truncated)
            hash_display = file_data.get('file_hash', 'N/A')[:12] + '...' if file_data.get('file_hash') else 'N/A'

            data.append([
                str(idx),
                file_display,
                hash_display,
                file_data.get('date_taken', '')[:10] if file_data.get('date_taken') else 'N/A',
                file_data['file_type'].upper(),
                '⚠' if file_data.get('is_flagged') else ''
            ])

        table = Table(data, colWidths=[0.3*inch, 2.2*inch, 1.2*inch, 0.8*inch, 0.5*inch, 0.4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0066FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        
        if len(files) > 50:
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(
                f"Note: Showing first 50 of {len(files)} total files.",
                styles['Footer']
            ))
        
        return story
    
    def _build_ai_analysis(self, files: List[Dict], styles) -> List:
        """Build AI analysis results section"""
        story = []
        
        story.append(Paragraph("AI Analysis Results", styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        # Get analyzed files
        analyzed = [f for f in files if f.get('ai_processed')]
        
        if not analyzed:
            story.append(Paragraph("No AI analysis has been performed yet.", styles['Normal']))
            return story
        
        # Tag frequency analysis
        all_tags = []
        for file_data in analyzed:
            if file_data.get('ai_tags'):
                try:
                    tags = json.loads(file_data['ai_tags'])
                    all_tags.extend(tags)
                except:
                    pass
        
        if all_tags:
            from collections import Counter
            tag_counts = Counter(all_tags)
            top_tags = tag_counts.most_common(10)
            
            story.append(Paragraph("Top 10 Detected Tags:", styles['CustomSubHeading']))
            story.append(Spacer(1, 0.1*inch))
            
            tag_data = [['Tag', 'Occurrences']]
            for tag, count in top_tags:
                tag_data.append([tag, str(count)])
            
            tag_table = Table(tag_data, colWidths=[3*inch, 1.5*inch])
            tag_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F0F0')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            
            story.append(tag_table)
        
        # Face detection summary
        total_faces = sum(f.get('face_count', 0) for f in analyzed)
        files_with_faces = len([f for f in analyzed if f.get('face_count', 0) > 0])
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Face Detection Summary:", styles['CustomSubHeading']))
        story.append(Paragraph(
            f"Total faces detected: {total_faces}<br/>"
            f"Files containing faces: {files_with_faces}",
            styles['Normal']
        ))
        
        # OCR summary
        files_with_text = len([f for f in analyzed if f.get('ocr_text')])
        
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("Text Extraction Summary:", styles['CustomSubHeading']))
        story.append(Paragraph(
            f"Files with extracted text: {files_with_text}",
            styles['Normal']
        ))
        
        return story
    
    def _build_audit_trail(self, logs: List[Dict], styles) -> List:
        """Build audit trail section"""
        story = []
        
        story.append(Paragraph("Audit Trail", styles['CustomHeading']))
        story.append(Spacer(1, 0.1*inch))
        
        if not logs:
            story.append(Paragraph("No audit logs available.", styles['Normal']))
            return story
        
        # Build table
        data = [['Timestamp', 'User', 'Action']]
        
        for log in logs[:30]:  # Limit to 30
            timestamp = log['timestamp'].split('T')
            date_part = timestamp[0]
            time_part = timestamp[1][:8] if len(timestamp) > 1 else ''
            
            data.append([
                f"{date_part} {time_part}",
                log.get('user_name', 'System'),
                log['action'].replace('_', ' ').title()
            ])
        
        table = Table(data, colWidths=[1.5*inch, 1.5*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F0F0F0')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(table)
        
        return story
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#0066FF'))
        canvas.drawString(0.75*inch, letter[1] - 0.5*inch, "FORENSTIQ AI TECHNOLOGIES")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            letter[0] / 2,
            0.5*inch,
            f"Page {canvas.getPageNumber()} • Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        
        canvas.restoreState()