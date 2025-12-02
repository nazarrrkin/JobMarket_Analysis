import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { useState } from 'react';
import {
  Box,
  Button,
  Paper,
  Typography,
  LinearProgress,
  Alert,
  Container
} from '@mui/material';

const MainPage = () => {
  const [selectedFiles, setSelectedFiles] = useState<{ [key: string]: File | null }>({
    area: null,
    job_category: null,
    employees: null,
    vacancy: null,
  });
  const [uploadProgress, setUploadProgress] = useState(0);

  // Мутация для загрузки файлов
  const uploadFilesMutation = useMutation({
    mutationFn: async (files: { [key: string]: File }) => {
      const formData = new FormData();
      
      // Добавляем каждый файл с соответствующим ключом
      Object.entries(files).forEach(([key, file]) => {
        if (file) {
          formData.append(key, file);
        }
      });

      const response = await axios.post('http://127.0.0.1:8000/api/take-data/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const progress = (progressEvent.loaded / progressEvent.total) * 100;
            setUploadProgress(Math.round(progress));
          }
        },
      });

      return response.data;
    },
    onSuccess: (data) => {
      console.log('Файлы успешно загружены:', data);
      setSelectedFiles({
        area: null,
        job_category: null,
        employees: null,
        vacancy: null,
      });
      setUploadProgress(0);
    },
    onError: (error) => {
      console.error('Ошибка при загрузке файлов:', error);
    },
  });

  const handleFileChange = (tableKey: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      const file = event.target.files[0];
      
      // Проверяем, что файл CSV
      if (file.type !== 'text/csv' && !file.name.endsWith('.csv')) {
        alert('Пожалуйста, выберите CSV файл');
        return;
      }
      
      setSelectedFiles(prev => ({
        ...prev,
        [tableKey]: file
      }));
      setUploadProgress(0);
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    
    // Проверяем, что все файлы выбраны
    const allFilesSelected = Object.values(selectedFiles).every(file => file !== null);
    
    if (!allFilesSelected) {
      alert('Пожалуйста, выберите все 4 CSV файла');
      return;
    }

    uploadFilesMutation.mutate(selectedFiles as { [key: string]: File });
  };

  const fileConfigs = [
    { key: 'area', label: 'Файл для таблицы Области' },
    { key: 'job_category', label: 'Файл для таблицы Категорий работ' },
    { key: 'employees', label: 'Файл для таблицы Работники' },
    { key: 'vacancy', label: 'Файл для таблицы Вакансии' },
  ];

  return (
    <Container maxWidth="sm">
      <Paper 
        elevation={3} 
        sx={{ 
          padding: '32px', 
          marginTop: '40px',
          borderRadius: '12px'
        }}
      >
        <Typography 
          variant="h4" 
          component="h1" 
          sx={{ 
            marginBottom: '24px',
            textAlign: 'center',
            fontWeight: 'bold',
            color: '#1976d2'
          }}
        >
          Загрузка CSV файлов
        </Typography>

        <Typography 
          variant="body1" 
          sx={{ 
            marginBottom: '24px',
            textAlign: 'center',
            color: '#666'
          }}
        >
          Пожалуйста, загрузите 4 CSV файла для соответствующих таблиц
        </Typography>

        <form onSubmit={handleSubmit}>
          {fileConfigs.map((config) => (
            <Box key={config.key} sx={{ marginBottom: '16px' }}>
              <Typography variant="subtitle2" sx={{ marginBottom: '8px' }}>
                {config.label}
              </Typography>
              <input
                accept=".csv,text/csv"
                style={{ display: 'none' }}
                id={`${config.key}-file-input`}
                type="file"
                onChange={handleFileChange(config.key)}
              />
              <label htmlFor={`${config.key}-file-input`}>
                <Button 
                  variant="outlined" 
                  component="span"
                  fullWidth
                  sx={{
                    padding: '12px',
                    borderStyle: 'dashed',
                    borderWidth: '2px',
                    borderColor: selectedFiles[config.key] ? '#4caf50' : undefined
                  }}
                >
                  {selectedFiles[config.key] 
                    ? selectedFiles[config.key]!.name 
                    : `Выберите CSV файл`}
                </Button>
              </label>
            </Box>
          ))}

          {uploadProgress > 0 && uploadProgress < 100 && (
            <Box sx={{ marginBottom: '20px' }}>
              <LinearProgress 
                variant="determinate" 
                value={uploadProgress}
                sx={{ height: '8px', borderRadius: '4px' }}
              />
              <Typography 
                variant="body2" 
                sx={{ textAlign: 'center', marginTop: '8px' }}
              >
                {uploadProgress}%
              </Typography>
            </Box>
          )}

          <Button
            type="submit"
            variant="contained"
            fullWidth
            disabled={!Object.values(selectedFiles).every(file => file !== null) || uploadFilesMutation.isPending}
            sx={{
              padding: '12px',
              fontSize: '16px',
              fontWeight: 'bold',
              marginTop: '16px'
            }}
          >
            {uploadFilesMutation.isPending ? 'Загрузка...' : 'Загрузить все файлы'}
          </Button>
        </form>

        {uploadFilesMutation.isSuccess && (
          <Alert 
            severity="success" 
            sx={{ marginTop: '20px' }}
          >
            Все файлы успешно загружены!
          </Alert>
        )}

        {uploadFilesMutation.isError && (
          <Alert 
            severity="error" 
            sx={{ marginTop: '20px' }}
          >
            Ошибка при загрузке файлов
          </Alert>
        )}
      </Paper>
    </Container>
  );
};

export default MainPage;