import { describe, it, expect } from 'vitest';
import { formatPercentage, formatScore } from './utils';

describe('utils', () => {
  describe('formatPercentage', () => {
    it('formats numbers correctly', () => {
      expect(formatPercentage(44.4)).toBe('44.4%');
      expect(formatPercentage(100)).toBe('100.0%');
      expect(formatPercentage(0)).toBe('0.0%');
    });

    it('handles null and undefined', () => {
      expect(formatPercentage(null)).toBe('N/A');
      expect(formatPercentage(undefined)).toBe('N/A');
    });
  });

  describe('formatScore', () => {
    it('formats numbers correctly', () => {
      expect(formatScore(84.9)).toBe('84.9');
      expect(formatScore(0)).toBe('0.0');
    });

    it('handles null/undefined gracefully', () => {
      expect(formatScore(null)).toBe('N/A');
      expect(formatScore(undefined)).toBe('N/A');
    });
  });
});
