// Scan history service to manage user scans

// Product images mapping for real product photos
export const PRODUCT_IMAGES = {
  // Nike Air Max 270
  'Nike Air Max 270': 'https://static.nike.com/a/images/t_PDP_1280_v1/f_auto,q_auto:eco/ec87d9f5-e1cb-4f3b-90a1-6d25d770ae3c/air-max-270-mens-shoes-KkLcRc.png',
  'Air Max 270': 'https://static.nike.com/a/images/t_PDP_1280_v1/f_auto,q_auto:eco/ec87d9f5-e1cb-4f3b-90a1-6d25d770ae3c/air-max-270-mens-shoes-KkLcRc.png',
  
  // Gucci Marmont
  'Gucci Marmont Mini': 'https://media.gucci.com/style/DarkGray_Center_0_0_800x800/1648227729/476432_DTDCT_1000_001_100_0000_Light-GG-Marmont-mini-chain-bag.jpg',
  'Gucci': 'https://media.gucci.com/style/DarkGray_Center_0_0_800x800/1648227729/476432_DTDCT_1000_001_100_0000_Light-GG-Marmont-mini-chain-bag.jpg',
  
  // Apple Watch
  'Apple Watch Series 9': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MKU83_VW_34FR+watch-49-titanium-ultra2_VW_34FR_WF_CO?wid=1400&hei=1400&fmt=jpeg&qlt=95&.v=1694507915513',
  'Apple Watch': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MKU83_VW_34FR+watch-49-titanium-ultra2_VW_34FR_WF_CO?wid=1400&hei=1400&fmt=jpeg&qlt=95&.v=1694507915513',
  
  // Pharmaceuticals
  'Lagos Pharma Malaria Tablets': 'https://5.imimg.com/data5/SELLER/Default/2022/7/NL/MY/HY/1853310/malaria-tablets-500x500.jpg',
  'Malaria Tablets': 'https://5.imimg.com/data5/SELLER/Default/2022/7/NL/MY/HY/1853310/malaria-tablets-500x500.jpg',
  
  // Dairy products
  'Dano Milk 1L': 'https://www.danone.com/content/dam/danone-corp/danone-com/products/2022/danone-dairy-dano-milk-1l.png',
  'Dano Milk': 'https://www.danone.com/content/dam/danone-corp/danone-com/products/2022/danone-dairy-dano-milk-1l.png',
  'Peak Milk Powder': 'https://www.frieslandcampina.com.ng/wp-content/uploads/sites/7/2020/09/peak-1.png',
  
  // Food products
  'Indomie Noodles': 'https://www.indomie.com/wp-content/uploads/2021/03/indomie-chicken-1.png',
  'Indomie': 'https://www.indomie.com/wp-content/uploads/2021/03/indomie-chicken-1.png',
  
  // Beverages
  'Coca-Cola 50cl': 'https://www.coca-cola.com/content/dam/one-content/ng/en/products/coca-cola-original.png',
  'Coca-Cola': 'https://www.coca-cola.com/content/dam/one-content/ng/en/products/coca-cola-original.png',
  
  // Default fallback images by category
  'Footwear': 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=500',
  'Fashion': 'https://images.unsplash.com/photo-1539008835657-9e8e9680c956?w=500',
  'Electronics': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=500',
  'Pharmaceuticals': 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500',
  'Dairy': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500',
  'Food': 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500',
  'Beverages': 'https://images.unsplash.com/photo-1543253687-c931c8e01820?w=500',
};

// Save a new scan to history
export const saveScanToHistory = (scanData) => {
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  if (!currentUser.phone) return [];
  
  // Get existing history for this user
  const historyKey = `scanHistory_${currentUser.phone}`;
  const existingHistory = JSON.parse(localStorage.getItem(historyKey) || '[]');
  
  // Get product image
  const productImage = getProductImage(scanData.product, scanData.category);
  
  // Add new scan with timestamp and image
  const newScan = {
    id: `scan_${Date.now()}`,
    ...scanData,
    productImage: scanData.capturedImage || productImage, // Use captured image if available, otherwise default
    timestamp: new Date().toISOString(),
    userPhone: currentUser.phone
  };
  
  // Add to beginning of array (most recent first)
  const updatedHistory = [newScan, ...existingHistory];
  
  // Keep only last 50 scans to prevent localStorage overflow
  const trimmedHistory = updatedHistory.slice(0, 50);
  
  localStorage.setItem(historyKey, JSON.stringify(trimmedHistory));
  
  // Also mark that user has scanned
  localStorage.setItem('hasScanned', 'true');
  
  return trimmedHistory;
};

// Get product image based on name or category
export const getProductImage = (productName, category) => {
  // Try to find exact product match
  for (const [key, value] of Object.entries(PRODUCT_IMAGES)) {
    if (productName?.toLowerCase().includes(key.toLowerCase())) {
      return value;
    }
  }
  
  // Fallback to category image
  if (category && PRODUCT_IMAGES[category]) {
    return PRODUCT_IMAGES[category];
  }
  
  // Default fallback
  return 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=500';
};

// Get all scans for current user
export const getUserScanHistory = () => {
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  if (!currentUser.phone) return [];
  
  const historyKey = `scanHistory_${currentUser.phone}`;
  return JSON.parse(localStorage.getItem(historyKey) || '[]');
};

// Get recent scans (last 3 for home screen)
export const getRecentScans = (limit = 3) => {
  const allScans = getUserScanHistory();
  return allScans.slice(0, limit);
};

// Get scan by ID
export const getScanById = (scanId) => {
  const allScans = getUserScanHistory();
  return allScans.find(scan => scan.id === scanId);
};

// Clear all scan history for current user
export const clearScanHistory = () => {
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || '{}');
  if (!currentUser.phone) return;
  
  const historyKey = `scanHistory_${currentUser.phone}`;
  localStorage.removeItem(historyKey);
};

// Generate mock scan data for demo purposes with real images
export const generateMockScan = (isAuthentic = true) => {
  const products = [
    { 
      name: 'Nike Air Max 270', 
      category: 'Footwear', 
      manufacturer: 'Nike Inc.', 
      nafdac: 'B1-4022-XP',
      image: 'https://static.nike.com/a/images/t_PDP_1280_v1/f_auto,q_auto:eco/ec87d9f5-e1cb-4f3b-90a1-6d25d770ae3c/air-max-270-mens-shoes-KkLcRc.png'
    },
    { 
      name: 'Gucci Marmont Mini', 
      category: 'Fashion', 
      manufacturer: 'Gucci', 
      nafdac: 'B1-4023-XP',
      image: 'https://media.gucci.com/style/DarkGray_Center_0_0_800x800/1648227729/476432_DTDCT_1000_001_100_0000_Light-GG-Marmont-mini-chain-bag.jpg'
    },
    { 
      name: 'Apple Watch Series 9', 
      category: 'Electronics', 
      manufacturer: 'Apple Inc.', 
      nafdac: 'B1-4024-XP',
      image: 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MKU83_VW_34FR+watch-49-titanium-ultra2_VW_34FR_WF_CO?wid=1400&hei=1400&fmt=jpeg&qlt=95&.v=1694507915513'
    },
    { 
      name: 'Lagos Pharma Malaria Tablets', 
      category: 'Pharmaceuticals', 
      manufacturer: 'Lagos Pharma Ltd.', 
      nafdac: 'B1-4025-XP',
      image: 'https://5.imimg.com/data5/SELLER/Default/2022/7/NL/MY/HY/1853310/malaria-tablets-500x500.jpg'
    },
    { 
      name: 'Dano Milk 1L', 
      category: 'Dairy', 
      manufacturer: 'Dano Foods', 
      nafdac: 'B1-4026-XP',
      image: 'https://www.danone.com/content/dam/danone-corp/danone-com/products/2022/danone-dairy-dano-milk-1l.png'
    },
    { 
      name: 'Indomie Noodles', 
      category: 'Food', 
      manufacturer: 'Dufil Prima Foods', 
      nafdac: 'B1-4027-XP',
      image: 'https://www.indomie.com/wp-content/uploads/2021/03/indomie-chicken-1.png'
    },
    { 
      name: 'Coca-Cola 50cl', 
      category: 'Beverages', 
      manufacturer: 'Nigerian Bottling Company', 
      nafdac: 'B1-4028-XP',
      image: 'https://www.coca-cola.com/content/dam/one-content/ng/en/products/coca-cola-original.png'
    },
    { 
      name: 'Peak Milk Powder', 
      category: 'Dairy', 
      manufacturer: 'FrieslandCampina', 
      nafdac: 'B1-4029-XP',
      image: 'https://www.frieslandcampina.com.ng/wp-content/uploads/sites/7/2020/09/peak-1.png'
    }
  ];
  
  const randomProduct = products[Math.floor(Math.random() * products.length)];
  const randomHour = Math.floor(Math.random() * 12) + 1;
  const randomMinute = Math.floor(Math.random() * 60);
  const ampm = Math.random() > 0.5 ? 'AM' : 'PM';
  const timeString = `${randomHour}:${randomMinute.toString().padStart(2, '0')} ${ampm}`;
  
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  
  const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  const randomDay = Math.random() > 0.3 ? 'Today' : Math.random() > 0.5 ? 'Yesterday' : days[Math.floor(Math.random() * 7)];
  
  return {
    id: `scan_mock_${Date.now()}_${Math.random()}`,
    product: randomProduct.name,
    productImage: randomProduct.image,
    category: randomProduct.category,
    manufacturer: randomProduct.manufacturer,
    nafdacNumber: randomProduct.nafdac,
    status: isAuthentic ? 'authentic' : (Math.random() > 0.5 ? 'caution' : 'fake'),
    time: randomDay === 'Today' ? `Today, ${timeString}` : randomDay === 'Yesterday' ? `Yesterday, ${timeString}` : `${randomDay}, ${timeString}`,
    verified: isAuthentic ? true : Math.random() > 0.7,
    similarity: isAuthentic ? Math.floor(Math.random() * 20) + 80 : Math.floor(Math.random() * 50) + 30,
    batchNumber: `BATCH-${Math.floor(Math.random() * 1000)}`,
    expiryDate: `2026-0${Math.floor(Math.random() * 9) + 1}`,
    location: ['Lagos Market', 'Kano Central', 'Abuja Mall', 'Port Harcourt Plaza', 'Ibadan Store'][Math.floor(Math.random() * 5)],
    timestamp: new Date().toISOString()
  };
};