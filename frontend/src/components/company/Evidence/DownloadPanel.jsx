import React, { useState } from 'react';
import Card from '../../common/Card';
import Icon from '../../common/Icon';
import Button from '../../common/Button';
import { downloadFile, getEvidenceFiles, createEvidenceZip } from '../../../services/downloadService';

const DownloadPanel = ({ selectedCase, onDownloadAll }) => {
  const [downloading, setDownloading] = useState(false);
  const [downloadingSingle, setDownloadingSingle] = useState(null);

  const handleDownloadAll = async () => {
    if (!selectedCase) return;
    
    setDownloading(true);
    
    // Get evidence files
    const files = getEvidenceFiles(selectedCase);
    
    // Create ZIP (simulated)
    const result = await createEvidenceZip(selectedCase, files);
    
    setDownloading(false);
    
    if (onDownloadAll) {
      onDownloadAll(result);
    }
  };

  const handleDownloadFile = (file) => {
    setDownloadingSingle(file.id);
    
    setTimeout(() => {
      if (file.type === 'image') {
        window.open(file.url, '_blank');
      } else {
        const content = `This is a sample ${file.name} file for case ${selectedCase}`;
        downloadFile(content, file.name, 'text/plain');
      }
      
      setDownloadingSingle(null);
    }, 500);
  };

  // Mock files for the selected case
  const getFilesForCase = () => {
    if (!selectedCase) return [];
    
    return [
      {
        id: 1,
        name: 'product-front.jpg',
        type: 'image',
        size: '2.4 MB',
        url: 'https://images.unsplash.com/photo-1549298916-b41d501d3772?w=400'
      },
      {
        id: 2,
        name: 'product-back.jpg',
        type: 'image',
        size: '1.8 MB',
        url: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400'
      },
      {
        id: 3,
        name: 'forensic-report.pdf',
        type: 'pdf',
        size: '856 KB'
      },
      {
        id: 4,
        name: 'scan-analysis.json',
        type: 'json',
        size: '124 KB'
      }
    ];
  };

  const files = getFilesForCase();

  return (
    <Card className="sticky top-6">
      <h3 className="font-semibold text-lg mb-4">Download Options</h3>
      
      {selectedCase ? (
        <>
          <div className="space-y-3 mb-4">
            {files.map((file) => (
              <button
                key={file.id}
                onClick={() => handleDownloadFile(file)}
                disabled={downloadingSingle === file.id}
                className="w-full flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors disabled:opacity-50"
              >
                <div className="flex items-center gap-3">
                  <Icon 
                    name={file.type === 'image' ? 'Image' : file.type === 'pdf' ? 'FileText' : 'File'} 
                    size={18} 
                    className={file.type === 'image' ? 'text-primary' : file.type === 'pdf' ? 'text-danger' : 'text-gray-500'} 
                    library="fi" 
                  />
                  <div className="text-left">
                    <p className="text-sm font-medium">{file.name}</p>
                    <p className="text-xs text-gray-400">{file.size}</p>
                  </div>
                </div>
                {downloadingSingle === file.id ? (
                  <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Icon name="Download" size={16} className="text-gray-400" library="fi" />
                )}
              </button>
            ))}
          </div>

          <div className="border-t border-gray-100 pt-4">
            <Button 
              variant="primary" 
              fullWidth 
              icon="Download"
              onClick={handleDownloadAll}
              disabled={downloading}
            >
              {downloading ? (
                <div className="flex items-center justify-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Creating ZIP...
                </div>
              ) : (
                'Download All (ZIP)'
              )}
            </Button>
            <p className="text-xs text-gray-400 text-center mt-2">
              {files.length} files • ~{(files.reduce((acc, f) => {
                const size = parseFloat(f.size);
                return acc + (f.size.includes('MB') ? size : size / 1024);
              }, 0)).toFixed(1)} MB total
            </p>
          </div>
        </>
      ) : (
        <div className="text-center py-8">
          <Icon name="Folder" size={32} className="text-gray-300 mx-auto mb-3" library="fi" />
          <p className="text-sm text-gray-400">Select a case to view files</p>
        </div>
      )}
    </Card>
  );
};

export default DownloadPanel;