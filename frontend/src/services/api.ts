// API Service Layer for Padhai Check Backend
import { BACKEND_CONFIG, getEndpointURL } from '../config/backend.config';

const BASE_URL = BACKEND_CONFIG.BASE_URL;
const USE_MOCK_FALLBACK = BACKEND_CONFIG.USE_MOCK_FALLBACK;

export interface VerificationResult {
  verdict: 'True' | 'False' | 'Misleading' | 'Unverified';
  explanation: string;
  evidence: Evidence[];
  wellbeing_message?: string;
}

export interface Evidence {
  source: string;
  snippet: string;
  url?: string;
}

export interface TrendingClaim {
  id: string;
  claim: string;
  verdict: 'True' | 'False' | 'Misleading' | 'Unverified';
  timestamp: string;
  views: number;
}

export interface HistoryItem {
  id: string;
  query: string;
  verdict: 'True' | 'False' | 'Misleading' | 'Unverified';
  timestamp: string;
  hasImage: boolean;
}

export interface ClaimDetails {
  id: string;
  claim: string;
  verdict: 'True' | 'False' | 'Misleading' | 'Unverified';
  explanation: string;
  evidence: Evidence[];
  timestamp: string;
  wellbeing_message?: string;
}

// Helper mapper functions
function mapClaimResultToVerificationResult(claim: any): VerificationResult {
  return {
    verdict: claim.verdict as VerificationResult['verdict'],
    explanation: claim.explanation_english || claim.explanation_hinglish || claim.explanation || '',
    evidence: (claim.evidence || []).map((e: any) => ({
      source: e.source || 'Unknown',
      snippet: e.snippet || e.text || '',
      url: e.url || undefined,
    })),
    wellbeing_message: claim.wellbeing_message || undefined,
  };
}

function mapTrendsResponseToTrendingClaims(resp: any): TrendingClaim[] {
  const list = resp.trending_claims || [];
  return list.map((t: any) => ({
    id: (t.claim ? encodeURIComponent(t.claim) : Math.random().toString(36).slice(2)) + '_' + (t.first_seen || Date.now()),
    claim: t.claim,
    verdict: t.verdict,
    timestamp: t.last_seen || t.first_seen || new Date().toISOString(),
    views: t.count || 0,
  }));
}

function mapClaimResultToClaimDetails(claim: any): ClaimDetails {
  return {
    id: claim.id,
    claim: claim.claim,
    verdict: claim.verdict,
    explanation: claim.explanation_english || claim.explanation_hinglish || claim.explanation || '',
    evidence: (claim.evidence || []).map((e: any) => ({
      source: e.source || 'Unknown',
      snippet: e.snippet || e.text || '',
      url: e.url || undefined,
    })),
    timestamp: claim.created_at || claim.timestamp || new Date().toISOString(),
    wellbeing_message: claim.wellbeing_message || undefined,
  };
}

// Upload file to backend
// POST /api/upload
export async function uploadFile(file: File): Promise<{ file_id: string }> {
  if (USE_MOCK_FALLBACK) {
    // Return a mock file_id for development; callers should treat this as an opaque id
    const mockId = `mock_${Date.now()}_${Math.random().toString(36).slice(2)}`;
    console.log('Using mock file_id for upload:', mockId);
    return { file_id: mockId };
  }

  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(getEndpointURL(BACKEND_CONFIG.ENDPOINTS.UPLOAD), {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload file');
    }

    const data = await response.json();
    // Backend UploadResponse returns { file_id, filename, content_type, extracted_text, message }
    return { file_id: data.file_id };
  } catch (error) {
    console.error('Upload error:', error);
    // As a final fallback, return a mock id so UX isn't blocked
    const fallbackId = `mock_fallback_${Date.now()}`;
    return { file_id: fallbackId };
  }
}

// Verify claim/question with optional files
// POST /api/verify
// Expected request body: { text?: string, file_urls?: string[] }
// Expected response: { verdict, explanation, evidence, wellbeing_message? }
export async function verifyContent(params: {
  text?: string;
  file_urls?: string[];
}): Promise<VerificationResult> {
  // Normalize params to the backend shape: { text?, file_ids? }
  const body: any = {};
  if (params.text) body.text = params.text;
  if (params.file_urls && params.file_urls.length > 0) body.file_ids = params.file_urls; // callers will pass file_ids array here

  if (USE_MOCK_FALLBACK) {
    // Use mock data directly if fallback is enabled
    console.log('Using mock data for verification');
    await new Promise(resolve => setTimeout(resolve, 1500)); // Simulate network delay
    return getMockVerificationResult(params);
  }

  console.log('Attempting to call backend /api/verify with body:', body);

  try {
    const endpoint = getEndpointURL(BACKEND_CONFIG.ENDPOINTS.VERIFY);
    console.log('Endpoint URL:', endpoint);

    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    console.log('Backend response status:', response.status);
    console.log('Backend response ok:', response.ok);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend error response:', errorText);
      throw new Error(`Backend returned ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    console.log('Backend returned data:', data);

    // Map backend ClaimResult -> VerificationResult
    const result = mapClaimResultToVerificationResult(data);
    console.log('Mapped result:', result);
    return result;
  } catch (error) {
    console.error('Verification error:', error);
    console.error('Error details:', {
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : 'N/A'
    });

    // Do NOT fallback to mock - throw error so we can see what's wrong
    throw error;
  }
}

// Get trending claims
// GET /api/trends
// Expected response: Array of { id, claim, verdict, timestamp, views }
export async function getTrendingClaims(): Promise<TrendingClaim[]> {
  if (USE_MOCK_FALLBACK) {
    // Use mock data directly if fallback is enabled
    console.log('Using mock data for trends');
    return getMockTrends();
  }

  try {
    console.log('Fetching trends from backend...');
    const response = await fetch(getEndpointURL(BACKEND_CONFIG.ENDPOINTS.TRENDS));

    console.log('Trends response status:', response.status);

    if (!response.ok) {
      throw new Error('Failed to fetch trending claims');
    }

    const data = await response.json();
    console.log('Backend trends response:', data);

    // Backend returns { trending_claims: [...], total_claims_checked, most_common_category }
    return mapTrendsResponseToTrendingClaims(data);
  } catch (error) {
    console.error('Trends error:', error);
    console.log('Falling back to mock trends');
    // Fallback to mock for development
    return getMockTrends();
  }
}

// Get claim details by ID
// GET /api/claim/{id}
// Expected response: { id, claim, verdict, explanation, evidence, timestamp, wellbeing_message? }
export async function getClaimDetails(id: string): Promise<ClaimDetails> {
  if (USE_MOCK_FALLBACK) {
    // Use mock data directly if fallback is enabled
    console.log('Using mock data for claim details');
    return getMockClaimDetails(id);
  }

  try {
    const response = await fetch(getEndpointURL(BACKEND_CONFIG.ENDPOINTS.CLAIM_DETAILS(id)));

    if (!response.ok) {
      throw new Error('Failed to fetch claim details');
    }

    const data = await response.json();
    return mapClaimResultToClaimDetails(data);
  } catch (error) {
    console.error('Claim details error:', error);
    // Fallback to mock for development
    return getMockClaimDetails(id);
  }
}

// Get verification history (from backend now)
export async function getHistory(): Promise<HistoryItem[]> {
  if (USE_MOCK_FALLBACK) {
    // Use mock data directly if fallback is enabled
    console.log('Using mock data for history');
    return getMockHistory();
  }

  try {
    const response = await fetch(getEndpointURL('/api/history'));

    if (!response.ok) {
      throw new Error('Failed to fetch history from backend');
    }

    const data = await response.json();
    console.log('Backend history response:', data);

    // Backend returns { history: [...] }
    return data.history || [];
  } catch (error) {
    console.error('History fetch error:', error);
    // Fallback to mock if backend is unavailable
    console.log('Falling back to mock history');
    return getMockHistory();
  }
}

// Save to history (no longer needed - backend handles it)
// Kept for backward compatibility but now a no-op
export function saveToHistory(item: HistoryItem): void {
  // History is now automatically saved by backend when verifyContent() is called
  // This function is kept for backward compatibility with existing frontend code
  console.log('Note: History is now saved server-side automatically. No local storage save needed.');
}

// Mock data functions for development/fallback
function getMockVerificationResult(params: { text?: string; file_urls?: string[] }): VerificationResult {
  const verdicts: VerificationResult['verdict'][] = ['True', 'False', 'Misleading', 'Unverified'];
  const mockVerdict = verdicts[Math.floor(Math.random() * verdicts.length)];

  const wellbeingMessages = [
    'Remember to take breaks while studying! 📚',
    'You\'re doing great! Keep up the good work! 💪',
    'Don\'t forget to stay hydrated and get enough sleep! 💧',
    'Taking care of your mental health is just as important as studying! 🧠',
    undefined,
    undefined,
  ];

  return {
    verdict: mockVerdict,
    explanation: `Based on our AI analysis and cross-referencing with multiple sources, this claim appears to be ${mockVerdict.toLowerCase()}. ${params.text ? `Your query "${params.text}" has been evaluated against verified educational databases and expert resources.` : 'The uploaded content has been processed using OCR and fact-checked against reliable sources.'}`,
    evidence: [
      {
        source: 'National Center for Education Research',
        snippet: 'Studies show that regular study breaks improve retention by up to 25%. The optimal study session length is 25-50 minutes followed by a 5-10 minute break.',
        url: 'https://example.com/source1',
      },
      {
        source: 'Journal of Educational Psychology',
        snippet: 'Research indicates that active recall and spaced repetition are among the most effective learning techniques for long-term memory formation.',
        url: 'https://example.com/source2',
      },
      {
        source: 'Indian Council of Medical Research',
        snippet: 'Adequate sleep (7-9 hours) is crucial for students as it consolidates learning and improves cognitive performance during exams.',
        url: 'https://example.com/source3',
      },
    ],
    wellbeing_message: wellbeingMessages[Math.floor(Math.random() * wellbeingMessages.length)],
  };
}

function getMockTrends(): TrendingClaim[] {
  return [
    {
      id: '1',
      claim: 'Drinking water during exams improves performance by 15%',
      verdict: 'True',
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      views: 1247,
    },
    {
      id: '2',
      claim: 'Studying at night is more effective than morning study',
      verdict: 'Misleading',
      timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
      views: 892,
    },
    {
      id: '3',
      claim: 'Blue light from phones damages memory retention',
      verdict: 'False',
      timestamp: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
      views: 756,
    },
    {
      id: '4',
      claim: 'CBSE will cancel all board exams this year',
      verdict: 'False',
      timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
      views: 2341,
    },
    {
      id: '5',
      claim: 'Listening to classical music while studying improves focus',
      verdict: 'Unverified',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      views: 534,
    },
  ];
}

function getMockClaimDetails(id: string): ClaimDetails {
  return {
    id,
    claim: 'Drinking water during exams improves performance by 15%',
    verdict: 'True',
    explanation: 'Multiple scientific studies have confirmed that proper hydration during cognitive tasks, including exams, can improve performance. A University of East London study found that students who brought water into exams performed 5% better on average. The 15% figure specifically comes from research on prolonged cognitive tasks where dehydration effects are more pronounced.',
    evidence: [
      {
        source: 'University of East London - Psychology Department',
        snippet: 'The study involving 447 students found that those who brought drinks, particularly water, into the exam hall achieved better grades, with improvements of up to 5% in their overall scores.',
        url: 'https://example.com/uel-study',
      },
      {
        source: 'Journal of Nutrition - Hydration and Cognitive Function',
        snippet: 'Research demonstrates that even mild dehydration (1-2% body water loss) can impair cognitive performance, including attention, memory, and mood.',
        url: 'https://example.com/nutrition-journal',
      },
      {
        source: 'American Journal of Clinical Nutrition',
        snippet: 'Adequate hydration is associated with improved cognitive performance across various tasks, with effects most pronounced during sustained mental effort.',
        url: 'https://example.com/ajcn',
      },
    ],
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    wellbeing_message: 'Stay hydrated during your study sessions! 💧',
  };
}

function getMockHistory(): HistoryItem[] {
  return [
    {
      id: 'h1',
      query: 'Is photosynthesis affected by moon phases?',
      verdict: 'False',
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      hasImage: false,
    },
    {
      id: 'h2',
      query: 'Does drinking coffee before exams help?',
      verdict: 'Misleading',
      timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      hasImage: false,
    },
    {
      id: 'h3',
      query: 'Uploaded screenshot: Math problem solution',
      verdict: 'True',
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      hasImage: true,
    },
    {
      id: 'h4',
      query: 'Are all prime numbers odd?',
      verdict: 'False',
      timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      hasImage: false,
    },
    {
      id: 'h5',
      query: 'Uploaded PDF: Chemistry notes verification',
      verdict: 'True',
      timestamp: new Date(Date.now() - 48 * 60 * 60 * 1000).toISOString(),
      hasImage: true,
    },
  ];
}
