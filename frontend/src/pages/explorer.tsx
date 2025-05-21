import React, { useState, useEffect } from 'react';
import { Box, Container, Typography, Grid, Paper, Tabs, Tab, Button, CircularProgress, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import Head from 'next/head';
import axios from 'axios';
import GPTChatPanel from '../components/GPTChatPanel';

// Declare process for TypeScript
declare const process: {
  env: {
    NEXT_PUBLIC_API_URL?: string;
  }
};

// API base URL - would come from environment variables in production
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

// Mock data for development
const MOCK_TIERS = {
  tier1: ['10027', '94110', '90220', '60614', '33139'],
  tier2: ['30318', '60619', '80202', '98101', '85004'],
  tier3: ['19103', '27601', '55401', '37203', '20005']
};

export default function Explorer() {
  const [selectedTier, setSelectedTier] = useState('tier1');
  const [selectedZip, setSelectedZip] = useState('');
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);
  const [zipData, setZipData] = useState(null);
  const [error, setError] = useState('');

  // Load ZIP codes for the selected tier
  const zipCodes = MOCK_TIERS[selectedTier] || [];

  // Set the first ZIP code when tier changes
  useEffect(() => {
    if (zipCodes.length > 0 && !zipCodes.includes(selectedZip)) {
      setSelectedZip(zipCodes[0]);
    }
  }, [selectedTier, zipCodes, selectedZip]);

  // Fetch data when ZIP code changes
  useEffect(() => {
    if (selectedZip) {
      fetchZipData(selectedZip);
    }
  }, [selectedZip]);

  const fetchZipData = async (zip) => {
    setLoading(true);
    setError('');

    try {
      // In a real app, this would fetch from your API
      const response = await axios.get(`${API_BASE_URL}/sentiment/${zip}`);
      setZipData(response.data);
    } catch (err) {
      console.error('Error fetching ZIP data:', err);
      setError('Failed to fetch neighborhood data');
      setZipData(null);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleTierChange = (event) => {
    setSelectedTier(event.target.value);
  };

  const handleZipChange = (event) => {
    setSelectedZip(event.target.value);
  };

  const handleRefresh = () => {
    if (selectedZip) {
      fetchZipData(selectedZip);
    }
  };

  return (
    <>
      <Head>
        <title>Neighborhood Explorer | Real Estate AI</title>
        <meta name="description" content="Explore neighborhood data and sentiment analysis" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Neighborhood Explorer
          </Typography>

          <Grid container spacing={3}>
            {/* Controls */}
            <Grid item xs={12}>
              <Paper elevation={2} sx={{ p: 3 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} sm={4} md={3}>
                    <FormControl fullWidth>
                      <InputLabel id="tier-select-label">Priority Tier</InputLabel>
                      <Select
                        labelId="tier-select-label"
                        value={selectedTier}
                        label="Priority Tier"
                        onChange={handleTierChange}
                      >
                        <MenuItem value="tier1">Tier 1 (High Priority)</MenuItem>
                        <MenuItem value="tier2">Tier 2 (Medium Priority)</MenuItem>
                        <MenuItem value="tier3">Tier 3 (Low Priority)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={4} md={3}>
                    <FormControl fullWidth>
                      <InputLabel id="zip-select-label">ZIP Code</InputLabel>
                      <Select
                        labelId="zip-select-label"
                        value={selectedZip}
                        label="ZIP Code"
                        onChange={handleZipChange}
                      >
                        {zipCodes.map((zip) => (
                          <MenuItem key={zip} value={zip}>{zip}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={12} sm={4} md={3}>
                    <Button 
                      variant="contained" 
                      color="primary" 
                      onClick={handleRefresh}
                      disabled={loading}
                      fullWidth
                    >
                      {loading ? <CircularProgress size={24} /> : 'Refresh Data'}
                    </Button>
                  </Grid>
                </Grid>
              </Paper>
            </Grid>

            {/* Main content */}
            <Grid item xs={12}>
              {error ? (
                <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
                  <Typography color="error">{error}</Typography>
                  <Button variant="outlined" color="primary" sx={{ mt: 2 }} onClick={handleRefresh}>
                    Try Again
                  </Button>
                </Paper>
              ) : loading ? (
                <Paper elevation={3} sx={{ p: 5, textAlign: 'center' }}>
                  <CircularProgress />
                  <Typography sx={{ mt: 2 }}>Loading neighborhood data...</Typography>
                </Paper>
              ) : zipData ? (
                <Paper elevation={3} sx={{ p: 0 }}>
                  <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                    <Tabs value={tabValue} onChange={handleTabChange} aria-label="neighborhood data tabs">
                      <Tab label="Overview" />
                      <Tab label="Sentiment Trends" />
                      <Tab label="Keywords & Topics" />
                      <Tab label="Visualizations" />
                      <Tab label="AI Assistant" />
                    </Tabs>
                  </Box>
                  
                  {/* Tab content */}
                  <Box sx={{ p: 3 }}>
                    {tabValue === 0 && (
                      <OverviewTab data={zipData} />
                    )}
                    
                    {tabValue === 1 && (
                      <TrendsTab data={zipData} />
                    )}
                    
                    {tabValue === 2 && (
                      <KeywordsTab data={zipData} />
                    )}
                    
                    {tabValue === 3 && (
                      <VisualizationsTab data={zipData} />
                    )}
                    
                    {tabValue === 4 && (
                      <AIAssistantTab zipCode={selectedZip} data={zipData} />
                    )}
                  </Box>
                </Paper>
              ) : (
                <Paper elevation={3} sx={{ p: 3, textAlign: 'center' }}>
                  <Typography>Select a ZIP code to view neighborhood data</Typography>
                </Paper>
              )}
            </Grid>
          </Grid>
        </Box>
      </Container>
    </>
  );
}

// Tab Components
function OverviewTab({ data }) {
  if (!data || !data.data) return <Typography>No data available</Typography>;
  
  const { data: zipData, zip_code } = data;
  
  return (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Typography variant="h4" gutterBottom>
          {zipData.City || 'Unknown City'}, {zipData.State || 'Unknown State'}
        </Typography>
        <Typography variant="h6" color="text.secondary" gutterBottom>
          ZIP Code: {zip_code}
        </Typography>
        
        <Box sx={{ mt: 3 }}>
          <Typography variant="h5" gutterBottom>Sentiment Score</Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Box
              sx={{
                position: 'relative',
                display: 'inline-flex',
                mr: 3
              }}
            >
              <CircularProgress
                variant="determinate"
                value={zipData['Sentiment Score'] || 0}
                size={80}
                thickness={5}
                sx={{ color: getSentimentColor(zipData['Sentiment Score']) }}
              />
              <Box
                sx={{
                  top: 0,
                  left: 0,
                  bottom: 0,
                  right: 0,
                  position: 'absolute',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Typography variant="h6" component="div">
                  {Math.round(zipData['Sentiment Score'] || 0)}
                </Typography>
              </Box>
            </Box>
            <Typography variant="body1">
              {getSentimentDescription(zipData['Sentiment Score'] || 0)}
            </Typography>
          </Box>
        </Box>
        
        <Box sx={{ mt: 3 }}>
          <Typography variant="h5" gutterBottom>Data Sources</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {(zipData['Sources Used'] || []).map((source, index) => (
              <Chip key={`source-${index}`} label={source} />
            ))}
          </Box>
        </Box>
      </Grid>
      
      <Grid item xs={12} md={6}>
        <Paper elevation={1} sx={{ p: 2, height: '100%', bgcolor: '#f5f5f5' }}>
          <Typography variant="h5" gutterBottom>Neighborhood Summary</Typography>
          <Typography variant="body1">
            This neighborhood in {zipData.City || 'Unknown City'}, {zipData.State || 'Unknown State'} has an overall sentiment score of {Math.round(zipData['Sentiment Score'] || 0)}/100.
            {zipData['Trending Keywords']?.length > 0 && (
              <> People frequently mention keywords like "{zipData['Trending Keywords'].slice(0, 3).join('", "')}" when discussing this area.</>
            )}
            {zipData['Trending Topics']?.length > 0 && (
              <> Common topics of discussion include {zipData['Trending Topics'].slice(0, 2).join(' and ')}.</>
            )}
          </Typography>
          
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>Tier Classification</Typography>
            <Typography variant="body1">
              This ZIP code is classified as {zipData.Tier || 'Unknown Tier'} priority for monitoring.
            </Typography>
          </Box>
          
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>Last Updated</Typography>
            <Typography variant="body1">
              {zipData['Last Updated'] ? new Date(zipData['Last Updated']).toLocaleString() : 'Unknown'}
            </Typography>
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
}

function TrendsTab({ data }) {
  if (!data) return <Typography>No trend data available</Typography>;
  
  // In a real app, you would fetch historical trend data
  // For now, we'll use mock data
  const mockTrendData = {
    dates: ['2025-01', '2025-02', '2025-03', '2025-04', '2025-05'],
    scores: [65, 68, 72, 70, 75]
  };
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom>Sentiment Trends</Typography>
      <Typography variant="body1" paragraph>
        Track how neighborhood sentiment has changed over time.
      </Typography>
      
      <Paper elevation={1} sx={{ p: 3, height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          [Sentiment Trend Chart Would Appear Here]
          <br />
          Current Score: {data.data?.['Sentiment Score'] || 'N/A'}
          <br />
          Trend: {mockTrendData.scores[mockTrendData.scores.length - 1] > mockTrendData.scores[0] ? 'Improving' : 'Declining'}
        </Typography>
      </Paper>
      
      <Box sx={{ mt: 4 }}>
        <Typography variant="h6" gutterBottom>Recent Changes</Typography>
        <Paper elevation={1} sx={{ p: 2 }}>
          <Typography variant="body1">
            Sentiment has {mockTrendData.scores[mockTrendData.scores.length - 1] > mockTrendData.scores[0] ? 'improved' : 'declined'} by {Math.abs(mockTrendData.scores[mockTrendData.scores.length - 1] - mockTrendData.scores[0])} points over the last {mockTrendData.dates.length} months.
          </Typography>
        </Paper>
      </Box>
    </Box>
  );
}

function KeywordsTab({ data }) {
  if (!data || !data.data) return <Typography>No keyword data available</Typography>;
  
  const { data: zipData } = data;
  const keywords = zipData['Trending Keywords'] || [];
  const topics = zipData['Trending Topics'] || [];
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom>Keywords & Topics</Typography>
      <Typography variant="body1" paragraph>
        Discover what people are saying about this neighborhood.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Trending Keywords</Typography>
            {keywords.length > 0 ? (
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {keywords.map((keyword, index) => (
                  <Chip key={`keyword-${index}`} label={keyword} />
                ))}
              </Box>
            ) : (
              <Typography color="text.secondary">No keywords available</Typography>
            )}
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper elevation={1} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Trending Topics</Typography>
            {topics.length > 0 ? (
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {topics.map((topic, index) => (
                  <Paper key={index} elevation={0} sx={{ p: 2, bgcolor: '#f5f5f5' }}>
                    <Typography variant="body1">{topic}</Typography>
                  </Paper>
                ))}
              </Box>
            ) : (
              <Typography color="text.secondary">No topics available</Typography>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

function VisualizationsTab({ data }) {
  if (!data) return <Typography>No visualization data available</Typography>;
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom>Visualizations</Typography>
      <Typography variant="body1" paragraph>
        Visual representations of neighborhood sentiment and trends.
      </Typography>
      
      <Paper elevation={1} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Sentiment Map</Typography>
        <Box sx={{ height: 300, bgcolor: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            [Interactive Map Would Appear Here]
          </Typography>
        </Box>
      </Paper>
      
      <Paper elevation={1} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>Keyword Cloud</Typography>
        <Box sx={{ height: 300, bgcolor: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            [Keyword Cloud Would Appear Here]
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}

// Helper components
interface ChipProps {
  label: string;
  color?: string;
  key?: string;
}

const Chip = ({ label, color = 'default' }: ChipProps) => (
  <Box
    component="span"
    sx={{
      px: 2,
      py: 1,
      borderRadius: 4,
      fontSize: '0.875rem',
      fontWeight: 500,
      backgroundColor: color === 'primary' ? '#1976d2' : '#e0e0e0',
      color: color === 'primary' ? 'white' : 'inherit',
      display: 'inline-block',
    }}
  >
    {label}
  </Box>
);

// Helper functions
function getSentimentDescription(score) {
  if (score >= 80) return 'Excellent';
  if (score >= 70) return 'Very Good';
  if (score >= 60) return 'Good';
  if (score >= 50) return 'Average';
  if (score >= 40) return 'Below Average';
  if (score >= 30) return 'Poor';
  return 'Very Poor';
}

function getSentimentColor(score) {
  if (score >= 80) return '#4caf50'; // Green
  if (score >= 70) return '#8bc34a'; // Light Green
  if (score >= 60) return '#cddc39'; // Lime
  if (score >= 50) return '#ffeb3b'; // Yellow
  if (score >= 40) return '#ffc107'; // Amber
  if (score >= 30) return '#ff9800'; // Orange
  return '#f44336'; // Red
}

function AIAssistantTab({ zipCode, data }) {
  const [initialPrompt, setInitialPrompt] = useState('');
  
  useEffect(() => {
    if (data && data.data) {
      const zipData = data.data;
      const city = zipData.City || 'Unknown City';
      const state = zipData.State || 'Unknown State';
      const score = Math.round(zipData['Sentiment Score'] || 0);
      const sentiment = getSentimentDescription(score);
      
      // Create a context-aware initial prompt
      setInitialPrompt(`Tell me more about ${city}, ${state} (ZIP: ${zipCode}). The neighborhood has a ${sentiment.toLowerCase()} sentiment score of ${score}/100.`);
    }
  }, [zipCode, data]);
  
  return (
    <Box>
      <Typography variant="h5" gutterBottom>AI Assistant</Typography>
      <Typography variant="body1" paragraph>
        Ask questions about this neighborhood or get personalized recommendations.
      </Typography>
      
      <Paper elevation={1} sx={{ p: 3 }}>
        <GPTChatPanel initialPrompt={initialPrompt} />
      </Paper>
    </Box>
  );
}
