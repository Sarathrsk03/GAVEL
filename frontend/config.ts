
export const API_BASE_URL_SUMMARIZER = 'http://localhost:8010';
export const API_BASE_URL_FORGERY = 'http://localhost:8011';
export const API_BASE_URL_PRECEDENT = 'http://localhost:8012';
export const API_BASE_URL_DRAFT = 'http://localhost:8013';

export const ENDPOINTS = {
    SUMMARIZE: `${API_BASE_URL_SUMMARIZER}/summarize`,
    VERIFY: `${API_BASE_URL_FORGERY}/verify`,
    SEARCH: `${API_BASE_URL_PRECEDENT}/search`,
    DRAFT: `${API_BASE_URL_DRAFT}/draft`,
};
