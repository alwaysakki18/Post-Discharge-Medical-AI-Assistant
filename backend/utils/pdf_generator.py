"""
PDF report generator for patient discharge reports.
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from typing import Dict, Any
import io


class PatientReportGenerator:
    """Generate PDF reports for patient discharge information."""
    
    def __init__(self):
        """Initialize the PDF generator."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        # Only add styles if they don't exist
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f77b4'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ))
        
        if 'CustomBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=10,
                alignment=TA_JUSTIFY
            ))
    
    def generate_patient_report(self, patient_data: Dict[str, Any]) -> bytes:
        """
        Generate a PDF report for a patient.
        
        Args:
            patient_data: Dictionary containing patient information
            
        Returns:
            PDF file as bytes
        """
        # Create a BytesIO buffer
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18,
        )
        
        # Container for the 'Flowable' objects
        elements = []
        
        # Add title
        title = Paragraph("Post-Discharge Medical Report", self.styles['CustomTitle'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Add medical disclaimer
        disclaimer = Paragraph(
            "<b>⚠️ MEDICAL DISCLAIMER:</b> This report is for informational purposes only. "
            "Always consult with healthcare professionals for medical advice. "
            "In case of emergency, call 911 or go to the nearest emergency room.",
            ParagraphStyle(
                name='Disclaimer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.red,
                spaceAfter=20,
                borderColor=colors.red,
                borderWidth=1,
                borderPadding=10,
                backColor=colors.HexColor('#fff3cd')
            )
        )
        elements.append(disclaimer)
        elements.append(Spacer(1, 0.3*inch))
        
        # Patient Information Section
        elements.append(Paragraph("Patient Information", self.styles['SectionHeader']))
        
        patient_info_data = [
            ['Patient Name:', patient_data.get('patient_name', 'N/A')],
            ['Patient ID:', str(patient_data.get('patient_id', 'N/A'))],
            ['Discharge Date:', patient_data.get('discharge_date', 'N/A')],
            ['Report Generated:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
        ]
        
        patient_info_table = Table(patient_info_data, colWidths=[2*inch, 4*inch])
        patient_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(patient_info_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Primary Diagnosis
        elements.append(Paragraph("Primary Diagnosis", self.styles['SectionHeader']))
        diagnosis_text = Paragraph(
            patient_data.get('primary_diagnosis', 'N/A'),
            self.styles['CustomBodyText']
        )
        elements.append(diagnosis_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Medications
        elements.append(Paragraph("Prescribed Medications", self.styles['SectionHeader']))
        medications = patient_data.get('medications', [])
        if medications:
            for i, med in enumerate(medications, 1):
                med_text = Paragraph(f"{i}. {med}", self.styles['CustomBodyText'])
                elements.append(med_text)
        else:
            elements.append(Paragraph("No medications listed", self.styles['CustomBodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Dietary Restrictions
        elements.append(Paragraph("Dietary Restrictions", self.styles['SectionHeader']))
        dietary_text = Paragraph(
            patient_data.get('dietary_restrictions', 'No specific restrictions'),
            self.styles['CustomBodyText']
        )
        elements.append(dietary_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Follow-up Instructions
        elements.append(Paragraph("Follow-up Appointment", self.styles['SectionHeader']))
        followup_text = Paragraph(
            patient_data.get('follow_up', 'No follow-up scheduled'),
            self.styles['CustomBodyText']
        )
        elements.append(followup_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Warning Signs
        elements.append(Paragraph("⚠️ Warning Signs to Watch For", self.styles['SectionHeader']))
        warning_text = Paragraph(
            patient_data.get('warning_signs', 'No specific warnings'),
            ParagraphStyle(
                name='WarningStyle',
                parent=self.styles['CustomBodyText'],
                textColor=colors.HexColor('#d32f2f'),
                fontName='Helvetica-Bold'
            )
        )
        elements.append(warning_text)
        elements.append(Spacer(1, 0.2*inch))
        
        # Discharge Instructions
        elements.append(Paragraph("Discharge Instructions", self.styles['SectionHeader']))
        instructions_text = Paragraph(
            patient_data.get('discharge_instructions', 'Follow standard post-discharge care'),
            self.styles['CustomBodyText']
        )
        elements.append(instructions_text)
        elements.append(Spacer(1, 0.3*inch))
        
        # Footer
        elements.append(Spacer(1, 0.5*inch))
        footer = Paragraph(
            "This report was generated by the Post Discharge Medical AI Assistant. "
            "For questions or concerns, please contact your healthcare provider.",
            ParagraphStyle(
                name='Footer',
                parent=self.styles['Normal'],
                fontSize=9,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
        )
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes


# Global instance
pdf_generator = PatientReportGenerator()

def generate_patient_pdf(patient_data: Dict[str, Any]) -> bytes:
    """
    Generate a PDF report for a patient.
    
    Args:
        patient_data: Patient information dictionary
        
    Returns:
        PDF file as bytes
    """
    return pdf_generator.generate_patient_report(patient_data)
