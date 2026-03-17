import axios from 'axios';

const CLOUDINARY_URL = 'https://api.cloudinary.com/v1_1/YOUR_CLOUD_NAME/image/upload'; // Replace with your cloud name
const UPLOAD_PRESET = 'YOUR_UPLOAD_PRESET'; // Replace with your upload preset

export const uploadImageToCloudinary = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('upload_preset', UPLOAD_PRESET);
  
  try {
    const response = await axios.post(CLOUDINARY_URL, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return {
      success: true,
      url: response.data.secure_url,
      publicId: response.data.public_id
    };
  } catch (error) {
    console.error('Error uploading to Cloudinary:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

// For demo purposes, if you don't have Cloudinary set up, use this mock function
export const mockUploadImage = async (file) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      // Create a local object URL for demo
      const url = URL.createObjectURL(file);
      resolve({
        success: true,
        url: url,
        publicId: `demo_${Date.now()}`
      });
    }, 1500);
  });
};