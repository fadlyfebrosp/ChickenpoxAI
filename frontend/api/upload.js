import { handleUpload } from '@vercel/blob/client';

const MAX_IMAGE_SIZE = 10 * 1024 * 1024;
const ALLOWED_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/webp'];
const IMAGE_PATH_PATTERN = /^skin-images\/[0-9a-f-]{36}\.(jpg|png|webp)$/i;

export default async function handler(request, response) {
  response.setHeader('Cache-Control', 'no-store');

  if (request.method !== 'POST') {
    response.setHeader('Allow', 'POST');
    return response.status(405).json({ error: 'Method not allowed.' });
  }

  const allowedOrigins = [
    'https://chickenpox-ai.vercel.app',
    process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : null,
  ].filter(Boolean);
  if (!allowedOrigins.includes(request.headers.origin)) {
    return response.status(403).json({ error: 'Origin is not allowed to upload images.' });
  }

  try {
    const body = typeof request.body === 'string' ? JSON.parse(request.body) : request.body;
    const result = await handleUpload({
      body,
      request,
      onBeforeGenerateToken: async (pathname) => {
        if (!IMAGE_PATH_PATTERN.test(pathname)) {
          throw new Error('Invalid image path.');
        }

        return {
          allowedContentTypes: ALLOWED_CONTENT_TYPES,
          maximumSizeInBytes: MAX_IMAGE_SIZE,
          addRandomSuffix: true,
        };
      },
    });
    return response.status(200).json(result);
  } catch (error) {
    console.error('Blob image upload authorization failed:', error);
    return response.status(400).json({ error: 'Image upload could not be authorized.' });
  }
}
