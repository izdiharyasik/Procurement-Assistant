import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
});

export async function submitJob(mode, files) {
  const formData = new FormData();
  formData.append('mode', mode);
  files.forEach((file) => formData.append('files', file));
  const { data } = await api.post('/api/jobs', formData);
  return data;
}

export async function getJob(jobId) {
  const { data } = await api.get(`/api/jobs/${jobId}`);
  return data;
}

export function resolveUrl(path) {
  return `${api.defaults.baseURL}${path}`;
}
