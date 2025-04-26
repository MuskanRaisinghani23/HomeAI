import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Box,
  Paper,
  Typography,
  TextField,
  InputAdornment,
  Button,
  MenuItem,
  FormControl,
  InputLabel,
  Select,
  FormControlLabel,
  Switch,
} from '@mui/material';

import STATE_CITY_MAP from '../STATE_CITY_MAP';

const PROPERTY_TYPE_OPTIONS = ['Shared', 'Private'];

export default function PreferencesForm() {
  const localuser = localStorage.getItem('user') || '';
  let userEmail = "";
  if (!localuser) {
    console.error('No user email found in local storage.');
  }
  else{
    userEmail = JSON.parse(localuser).email;
  }

  // Row 1 state
  const [propertyType, setPropertyType] = useState('');
  const [bedrooms,     setBedrooms]     = useState('');
  const [bathrooms,    setBathrooms]    = useState('');

  // Row 2 state
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');

  // Row 3 state
  const [wantsAmenities, setWantsAmenities] = useState(false);
  const [getalerts,      setGetAlerts]      = useState(false);

  // Row 4 state (location)
  const stateOptions = Object.keys(STATE_CITY_MAP);
  const [selectedState, setSelectedState] = useState(stateOptions[0] || '');
  const [selectedCity,  setSelectedCity]  = useState('');
  const [cityOptions,   setCityOptions]   = useState(
    (STATE_CITY_MAP[stateOptions[0]] || []).slice(0, 15)
  );

  const base_url= "http://76.152.120.193:8001/"

  useEffect(() => {
    if (!userEmail) return;
    axios
      .get(base_url+'api/listing/user-preferences', { params: { user_email: userEmail } })
      .then(res => {
        const p = res.data;
        if (p && Object.keys(p).length) {
          setPropertyType(p.ROOM_TYPE   || '');
          setBedrooms    (p.BEDROOM     != null ? String(p.BEDROOM) : '');
          setBathrooms   (p.BATHROOM    != null ? String(p.BATHROOM) : '');
          setMinPrice    (p.MINPRICE    != null ? String(p.MINPRICE) : '');
          setMaxPrice    (p.MAXPRICE    != null ? String(p.MAXPRICE) : '');
          setWantsAmenities(Boolean(p.AMENITIES));
          setGetAlerts(false);

          if (p.CITY) {
            setSelectedState(p.CITY);
            const list = STATE_CITY_MAP[p.CITY] || [];
            setCityOptions(list.slice(0, 15));
          }
          if (p.LOCATION) {
            setSelectedCity(p.LOCATION);
          }
        }
      })
      .catch(console.error);
  }, [userEmail]);

  useEffect(() => {
    const list = STATE_CITY_MAP[selectedState] || [];
    setCityOptions(list.slice(0, 15));
    setSelectedCity(list[0] || '');
  }, [selectedState]);

  const handleSubmit = e => {
    e.preventDefault();
    let localValue = localStorage.getItem('user');
    let userEmail = "";
    if (localValue){
      let parsedValue = JSON.parse(localValue);
      userEmail = parsedValue.email;
    }
    if(!userEmail){
      alert('Please login to save your preferences.');
      return;
    }
    const payload = {
      user_email:     userEmail,
      room_type:      propertyType    || null,
      city:           selectedState   || null,
      location:       selectedCity    || null,
      amenities:      wantsAmenities  ? true : false,
      getalerts:      getalerts       ? true : false,
      bedroom:        bedrooms    !== '' ? Number(bedrooms) : null,
      bathroom:       bathrooms   !== '' ? Number(bathrooms) : null,
      minprice:       minPrice    !== '' ? Number(minPrice)  : null,
      maxprice:       maxPrice    !== '' ? Number(maxPrice)  : null,
    };

    axios
      .post(base_url+'api/listing/user-preferences', payload)
      .then(() => alert('Preferences saved!'))
      .catch(err => {
        console.error(err);
        alert('Failed to save preferences.');
      });
  };

  return (
    <Paper elevation={3} sx={{ maxWidth: 800, mx: 'auto', p: 4, mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        Your Property Preferences
      </Typography>

      <Box component="form" onSubmit={handleSubmit} noValidate>
        {/* Row 1 */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
          <FormControl sx={{ minWidth: 160, flex: '1 1 160px' }}>
            <InputLabel id="prop-type-label">Room Type</InputLabel>
            <Select
              labelId="prop-type-label"
              value={propertyType}
              label="Room Type"
              onChange={e => setPropertyType(e.target.value)}
            >
              {PROPERTY_TYPE_OPTIONS.map(opt => (
                <MenuItem key={opt} value={opt}>{opt}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <TextField
            label="Bedrooms" type="number" size="small"
            value={bedrooms}
            onChange={e => setBedrooms(e.target.value)}
            sx={{ flex: '1 1 120px' }}
          />

          <TextField
            label="Bathrooms" type="number" size="small"
            value={bathrooms}
            onChange={e => setBathrooms(e.target.value)}
            sx={{ flex: '1 1 120px' }}
          />
        </Box>

        {/* Row 2 */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
          <TextField
            label="Min Price" type="number" size="small"
            value={minPrice}
            onChange={e => setMinPrice(e.target.value)}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>
            }}
            sx={{ flex: '1 1 200px' }}
          />
          <TextField
            label="Max Price" type="number" size="small"
            value={maxPrice}
            onChange={e => setMaxPrice(e.target.value)}
            InputProps={{
              startAdornment: <InputAdornment position="start">$</InputAdornment>
            }}
            sx={{ flex: '1 1 200px' }}
          />
        </Box>

        {/* Row 3 */}
        <Box sx={{ display: 'flex', gap: 4, alignItems: 'center', mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={wantsAmenities}
                onChange={e => setWantsAmenities(e.target.checked)}
              />
            }
            label="Require Amenities"
          />
          <FormControlLabel
            control={
              <Switch
                checked={getalerts}
                onChange={e => setGetAlerts(e.target.checked)}
              />
            }
            label="Get Alerts"
          />
        </Box>

        {/* Row 4 */}
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 3 }}>
          <FormControl sx={{ minWidth: 160, flex: '1 1 200px' }}>
            <InputLabel id="state-label">State</InputLabel>
            <Select
              labelId="state-label"
              value={selectedState}
              label="State"
              onChange={e => setSelectedState(e.target.value)}
            >
              {stateOptions.map(st => (
                <MenuItem key={st} value={st}>{st}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <FormControl sx={{ minWidth: 160, flex: '1 1 200px' }}>
            <InputLabel id="city-label">City</InputLabel>
            <Select
              labelId="city-label"
              value={selectedCity}
              label="City"
              onChange={e => setSelectedCity(e.target.value)}
            >
              {cityOptions.map(c => (
                <MenuItem key={c} value={c}>{c}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>

        {/* Submit */}
        <Box textAlign="right">
          <Button type="submit" variant="contained" size="large">
            Submit
          </Button>
        </Box>
      </Box>
    </Paper>
  );
}
