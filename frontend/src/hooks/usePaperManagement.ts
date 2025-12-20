// hooks/usePaperManagement.ts

import { useState, useCallback, useEffect } from 'react';
import type { Paper, PaperSection  } from '../types/paper';
import { paperService } from '../services/paperService';

export const usePaperManagement = () => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [activePaper, setActivePaper] = useState<Paper | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load papers from API/localStorage
  const loadPapers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const loadedPapers = await paperService.getAllPapers();
      setPapers(loadedPapers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load papers');
    } finally {
      setLoading(false);
    }
  }, []);

  // Create new paper
  const createPaper = useCallback(async (paperData: Partial<Paper>): Promise<Paper> => {
    setLoading(true);
    setError(null);
    try {
      const newPaper: Paper = {
        id: crypto.randomUUID(),
        title: paperData.title || 'Untitled Research Paper',
        abstract: paperData.abstract || '',
        status: 'draft',
        createdAt: new Date(),
        lastModified: new Date(),
        progress: 0,
        targetWordCount: paperData.targetWordCount || 8000,
        currentWordCount: 0,
        collaboratorCount: 0,
        researchArea: paperData.researchArea || '',
        sections: [
          { id: '1', title: 'Introduction', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 1 },
          { id: '2', title: 'Literature Review', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 2 },
          { id: '3', title: 'Methodology', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 3 },
          { id: '4', title: 'Results', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 4 },
          { id: '5', title: 'Discussion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 5 },
          { id: '6', title: 'Conclusion', content: '', status: 'not-started', lastModified: new Date(), wordCount: 0, order: 6 }
        ],
        tags: paperData.tags || [],
        isPublic: paperData.isPublic || false,
      };

      const savedPaper = await paperService.createPaper(newPaper);
      setPapers(prev => [...prev, savedPaper]);
      return savedPaper;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create paper');
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Update existing paper
  const updatePaper = useCallback(async (paperId: string, updates: Partial<Paper>) => {
    setLoading(true);
    setError(null);
    try {
      const updatedData = {
        ...updates,
        lastModified: new Date(),
      };

      const updatedPaper = await paperService.updatePaper(paperId, updatedData);
      
      setPapers(prev => prev.map(paper => 
        paper.id === paperId ? { ...paper, ...updatedData } : paper
      ));

      if (activePaper && activePaper.id === paperId) {
        setActivePaper(prev => prev ? { ...prev, ...updatedData } : null);
      }

      return updatedPaper;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update paper');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [activePaper]);

  // Delete paper
  const deletePaper = useCallback(async (paperId: string) => {
    setLoading(true);
    setError(null);
    try {
      await paperService.deletePaper(paperId);
      setPapers(prev => prev.filter(paper => paper.id !== paperId));
      
      if (activePaper && activePaper.id === paperId) {
        setActivePaper(null);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete paper');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [activePaper]);

  // Duplicate paper
  const duplicatePaper = useCallback(async (paperId: string, newTitle?: string) => {
    const originalPaper = papers.find(p => p.id === paperId);
    if (!originalPaper) throw new Error('Paper not found');

    const duplicatedPaper = await createPaper({
      ...originalPaper,
      title: newTitle || `${originalPaper.title} (Copy)`,
      status: 'draft',
      progress: 0,
      currentWordCount: 0,
    });

    return duplicatedPaper;
  }, [papers, createPaper]);

  // Archive paper
  const archivePaper = useCallback(async (paperId: string) => {
    return updatePaper(paperId, { status: 'archived' });
  }, [updatePaper]);

  // Update paper section
  const updatePaperSection = useCallback(async (paperId: string, sectionId: string, updates: Partial<PaperSection>) => {
    const paper = papers.find(p => p.id === paperId);
    if (!paper) throw new Error('Paper not found');

    const updatedSections = paper.sections.map(section =>
      section.id === sectionId 
        ? { ...section, ...updates, lastModified: new Date() }
        : section
    );

    // Calculate new progress based on completed sections
    const completedSections = updatedSections.filter(s => s.status === 'completed').length;
    const newProgress = Math.round((completedSections / updatedSections.length) * 100);

    // Calculate new word count
    const newWordCount = updatedSections.reduce((sum, section) => sum + section.wordCount, 0);

    return updatePaper(paperId, {
      sections: updatedSections,
      progress: newProgress,
      currentWordCount: newWordCount,
    });
  }, [papers, updatePaper]);

  // Get paper by ID
  const getPaperById = useCallback((paperId: string): Paper | undefined => {
    return papers.find(paper => paper.id === paperId);
  }, [papers]);

  // Filter papers
  const getFilteredPapers = useCallback((
    searchTerm: string = '',
    statusFilter: string = 'all',
    researchAreaFilter: string = 'all'
  ): Paper[] => {
    return papers.filter(paper => {
      const matchesSearch = searchTerm === '' || 
        paper.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        paper.researchArea.toLowerCase().includes(searchTerm.toLowerCase()) ||
        paper.coAuthors.some(author => author.toLowerCase().includes(searchTerm.toLowerCase()));

      const matchesStatus = statusFilter === 'all' || paper.status === statusFilter;
      const matchesResearchArea = researchAreaFilter === 'all' || paper.researchArea === researchAreaFilter;

      return matchesSearch && matchesStatus && matchesResearchArea;
    });
  }, [papers]);

  // Get paper statistics
  const getPaperStats = useCallback(() => {
    const totalPapers = papers.length;
    const publishedPapers = papers.filter(p => p.status === 'published').length;
    const draftPapers = papers.filter(p => p.status === 'draft').length;
    const inProgressPapers = papers.filter(p => ['in-progress', 'in-review', 'revision'].includes(p.status)).length;
    const totalWords = papers.reduce((sum, p) => sum + (p.currentWordCount || 0), 0);
    const avgProgress = totalPapers > 0 ? Math.round(papers.reduce((sum, p) => sum + p.progress, 0) / totalPapers) : 0;
    const totalCollaborators = new Set(papers.flatMap(p => p.coAuthors)).size;
    const researchAreas = new Set(papers.map(p => p.researchArea).filter(Boolean)).size;

    return {
      totalPapers,
      publishedPapers,
      draftPapers,
      inProgressPapers,
      totalWords,
      avgProgress,
      totalCollaborators,
      researchAreas,
      paperService,
    };
  }, [papers]);

  // Set active paper
  const selectPaper = useCallback((paper: Paper | null) => {
    setActivePaper(paper);
  }, []);

  // Initialize papers on mount
  useEffect(() => {
    loadPapers();
  }, [loadPapers]);

  return {
    papers,
    activePaper,
    loading,
    error,
    createPaper,
    updatePaper,
    deletePaper,
    duplicatePaper,
    archivePaper,
    updatePaperSection,
    getPaperById,
    getFilteredPapers,
    getPaperStats,
    selectPaper,
    loadPapers,
    setActivePaper: selectPaper,
  };
};