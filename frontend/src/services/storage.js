import { upload } from '@vercel/blob/client';

const MAX_IMAGE_SIZE = 10 * 1024 * 1024;
const EXTENSIONS_BY_TYPE = {
  'image/jpeg': 'jpg',
  'image/png': 'png',
  'image/webp': 'webp',
};

export async function storeImage(file) {
  const extension = EXTENSIONS_BY_TYPE[file.type];
  if (!extension || file.size > MAX_IMAGE_SIZE) {
    throw new Error('Choose a JPG, PNG, or WEBP image up to 10 MB.');
  }

  const path = `skin-images/${crypto.randomUUID()}.${extension}`;
  return upload(path, file, {
    access: 'public',
    handleUploadUrl: '/api/upload',
  });
}
