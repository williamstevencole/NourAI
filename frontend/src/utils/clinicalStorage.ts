import { ClinicalData } from '@/types/chat';

const CLINICAL_DATA_KEY = 'nutrirag_clinical_data';

export const clinicalStorage = {
  save(data: ClinicalData): void {
    try {
      localStorage.setItem(CLINICAL_DATA_KEY, JSON.stringify(data));
    } catch (error) {
      console.error('Error saving clinical data:', error);
    }
  },

  load(): ClinicalData | null {
    try {
      const data = localStorage.getItem(CLINICAL_DATA_KEY);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error loading clinical data:', error);
      return null;
    }
  },

  clear(): void {
    try {
      localStorage.removeItem(CLINICAL_DATA_KEY);
    } catch (error) {
      console.error('Error clearing clinical data:', error);
    }
  },

  exists(): boolean {
    return localStorage.getItem(CLINICAL_DATA_KEY) !== null;
  },
};
