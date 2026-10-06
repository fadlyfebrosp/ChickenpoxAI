import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 120000,
});

export async function analyzeImage(file, language = 'id') {
  const formData = new FormData();
  formData.append('image', file);
  formData.append('language', language);

  const response = await api.post('/predict', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}
