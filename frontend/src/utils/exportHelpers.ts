// utils/exportHelpers.ts
export const exportToJSON = (data: any, filename: string): void => {
  const jsonString = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonString], { type: 'application/json' });
  downloadBlob(blob, `${filename}.json`);
};

export const exportToCSV = (data: any[], filename: string): void => {
  if (data.length === 0) return;
  
  const headers = Object.keys(data[0]);
  const csvContent = [
    headers.join(','),
    ...data.map(row => headers.map(header => {
      const cell = row[header];
      if (typeof cell === 'string' && (cell.includes(',') || cell.includes('"'))) {
        return `"${cell.replace(/"/g, '""')}"`;
      }
      return cell;
    }).join(','))
  ].join('\n');
  
  const blob = new Blob([csvContent], { type: 'text/csv' });
  downloadBlob(blob, `${filename}.csv`);
};

export const exportToTXT = (content: string, filename: string): void => {
  const blob = new Blob([content], { type: 'text/plain' });
  downloadBlob(blob, `${filename}.txt`);
};

export const exportToPDF = async (element: HTMLElement, filename: string): Promise<void> => {
  // This would typically use a library like jsPDF or html2pdf
  console.log('PDF export would be implemented here with a library like jsPDF');
  alert(`PDF export for ${filename} would be generated`);
};

export const exportToLaTeX = (paper: any, filename: string): void => {
  const latexContent = generateLaTeXContent(paper);
  const blob = new Blob([latexContent], { type: 'text/plain' });
  downloadBlob(blob, `${filename}.tex`);
};

const downloadBlob = (blob: Blob, filename: string): void => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

const generateLaTeXContent = (paper: any): string => {
  return `\\documentclass{article}
\\usepackage[utf8]{inputenc}
\\usepackage{amsmath}
\\usepackage{amsfonts}
\\usepackage{amssymb}

\\title{${paper.title || 'Untitled Paper'}}
\\author{${paper.coAuthors ? paper.coAuthors.join(' \\and ') : 'Author'}}
\\date{\\today}

\\begin{document}

\\maketitle

\\begin{abstract}
${paper.abstract || 'Abstract content here...'}
\\end{abstract}

${paper.sections ? paper.sections.map((section: any) => `
\\section{${section.title}}
${section.content || 'Section content here...'}
`).join('\n') : ''}

\\end{document}`;
};

export const importFromFile = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      resolve(event.target?.result as string);
    };
    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
    reader.readAsText(file);
  });
};

export const validateFileType = (file: File, allowedTypes: string[]): boolean => {
  return allowedTypes.some(type => file.type.includes(type));
};

export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};