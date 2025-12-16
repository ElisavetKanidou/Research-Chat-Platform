"""
LaTeX export service
backend/app/services/latex_export_service.py
"""
from typing import Dict, List, Optional
import re


class LaTeXExportService:
    """Service for exporting papers to LaTeX format"""

    def __init__(self):
        self.document_classes = {
            'article': 'article',
            'paper': 'article',
            'thesis': 'report',
            'book': 'book'
        }

    def export_paper_to_latex(
        self,
        paper_data: Dict,
        document_class: str = 'article',
        include_bibliography: bool = True
    ) -> str:
        """Convert a paper to LaTeX format"""
        try:
            # Start building LaTeX document
            latex_content = []

            # Document class
            latex_content.append(f"\\documentclass[12pt,a4paper]{{{document_class}}}")
            latex_content.append("")

            # Packages
            packages = [
                "\\usepackage[utf8]{inputenc}",
                "\\usepackage[T1]{fontenc}",
                "\\usepackage{amsmath,amssymb}",
                "\\usepackage{graphicx}",
                "\\usepackage{hyperref}",
                "\\usepackage{cite}",
                "\\usepackage{booktabs}",  # For tables
                "\\usepackage{geometry}",
                "\\geometry{margin=1in}"
            ]
            latex_content.extend(packages)
            latex_content.append("")

            # Title, author, date
            title = self._escape_latex(paper_data.get('title', 'Untitled'))
            latex_content.append(f"\\title{{{title}}}")

            # Authors
            authors = paper_data.get('authors', [])
            if authors:
                author_str = " \\and ".join([self._escape_latex(a) for a in authors])
                latex_content.append(f"\\author{{{author_str}}}")
            else:
                latex_content.append("\\author{Author Name}")

            latex_content.append("\\date{\\today}")
            latex_content.append("")

            # Begin document
            latex_content.append("\\begin{document}")
            latex_content.append("")
            latex_content.append("\\maketitle")
            latex_content.append("")

            # Abstract
            abstract = paper_data.get('abstract', '')
            if abstract:
                latex_content.append("\\begin{abstract}")
                latex_content.append(self._escape_latex(abstract))
                latex_content.append("\\end{abstract}")
                latex_content.append("")

            # Sections
            sections = paper_data.get('sections', [])
            for section in sections:
                section_latex = self._convert_section_to_latex(section)
                latex_content.append(section_latex)
                latex_content.append("")

            # Bibliography
            if include_bibliography and paper_data.get('references'):
                latex_content.append(self._create_bibliography(paper_data['references']))

            # End document
            latex_content.append("\\end{document}")

            return "\n".join(latex_content)

        except Exception as e:
            print(f"❌ Failed to export to LaTeX: {str(e)}")
            raise

    def _convert_section_to_latex(self, section: Dict) -> str:
        """Convert a section to LaTeX format"""
        latex_lines = []

        # Section title
        title = self._escape_latex(section.get('title', ''))
        level = section.get('level', 1)

        if level == 1:
            latex_lines.append(f"\\section{{{title}}}")
        elif level == 2:
            latex_lines.append(f"\\subsection{{{title}}}")
        elif level == 3:
            latex_lines.append(f"\\subsubsection{{{title}}}")
        else:
            latex_lines.append(f"\\paragraph{{{title}}}")

        # Section content
        content = section.get('content', '')
        if content:
            # Convert markdown-like formatting to LaTeX
            latex_content = self._convert_content_to_latex(content)
            latex_lines.append(latex_content)

        return "\n".join(latex_lines)

    def _convert_content_to_latex(self, content: str) -> str:
        """Convert content with markdown-like formatting to LaTeX"""
        # Escape special LaTeX characters first
        text = self._escape_latex(content)

        # Convert **bold** to \textbf{}
        text = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', text)

        # Convert *italic* to \textit{}
        text = re.sub(r'\*(.+?)\*', r'\\textit{\1}', text)

        # Convert `code` to \texttt{}
        text = re.sub(r'`(.+?)`', r'\\texttt{\1}', text)

        # Convert [text](url) to \href{url}{text}
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'\\href{\2}{\1}', text)

        # Convert bullet lists
        text = self._convert_lists_to_latex(text)

        return text

    def _convert_lists_to_latex(self, text: str) -> str:
        """Convert markdown lists to LaTeX itemize/enumerate"""
        lines = text.split('\n')
        result = []
        in_list = False
        list_type = None

        for line in lines:
            # Check for bullet list
            if line.strip().startswith('- ') or line.strip().startswith('* '):
                if not in_list:
                    result.append('\\begin{itemize}')
                    in_list = True
                    list_type = 'itemize'
                item_text = line.strip()[2:]
                result.append(f'  \\item {item_text}')

            # Check for numbered list
            elif re.match(r'^\d+\.\s', line.strip()):
                if not in_list:
                    result.append('\\begin{enumerate}')
                    in_list = True
                    list_type = 'enumerate'
                item_text = re.sub(r'^\d+\.\s', '', line.strip())
                result.append(f'  \\item {item_text}')

            else:
                if in_list:
                    result.append(f'\\end{{{list_type}}}')
                    in_list = False
                    list_type = None
                result.append(line)

        # Close list if still open
        if in_list:
            result.append(f'\\end{{{list_type}}}')

        return '\n'.join(result)

    def _create_bibliography(self, references: List[Dict]) -> str:
        """Create bibliography section"""
        bib_lines = []

        bib_lines.append("\\begin{thebibliography}{99}")
        bib_lines.append("")

        for i, ref in enumerate(references, 1):
            # Format: \bibitem{ref1} Author, "Title," Publication, Year.
            authors = ', '.join(ref.get('authors', []))
            title = self._escape_latex(ref.get('title', ''))
            publication = ref.get('publication', '')
            year = ref.get('year', '')

            bib_entry = f"\\bibitem{{ref{i}}} {authors}, ``{title},'' "
            if publication:
                bib_entry += f"\\textit{{{publication}}}, "
            if year:
                bib_entry += f"{year}."

            # Add DOI or URL if available
            if ref.get('doi'):
                bib_entry += f" DOI: \\texttt{{{ref['doi']}}}"
            elif ref.get('url'):
                bib_entry += f" \\url{{{ref['url']}}}"

            bib_lines.append(bib_entry)
            bib_lines.append("")

        bib_lines.append("\\end{thebibliography}")

        return "\n".join(bib_lines)

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not text:
            return ""

        # Characters that need escaping in LaTeX
        replacements = {
            '\\': '\\textbackslash{}',
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}'
        }

        for char, replacement in replacements.items():
            text = text.replace(char, replacement)

        return text

    def export_to_file(
        self,
        paper_data: Dict,
        output_path: str,
        document_class: str = 'article'
    ) -> Dict:
        """Export paper to LaTeX file"""
        try:
            latex_content = self.export_paper_to_latex(
                paper_data,
                document_class=document_class
            )

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)

            return {
                'success': True,
                'file_path': output_path,
                'size': len(latex_content)
            }

        except Exception as e:
            print(f"❌ Failed to export LaTeX file: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


latex_export_service = LaTeXExportService()
