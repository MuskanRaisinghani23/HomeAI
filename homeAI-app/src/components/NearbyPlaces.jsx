import React, { useState } from 'react';

const typeIcons = {
  restaurant: '🍽️',
  cafe: '☕',
  park: '🌳',
  gym: '🏋️',
  supermarket: '🛒'
};

const NearbyPlaces = ({ nearbyPlaces }) => {
  const [activeType, setActiveType] = useState('restaurant'); // Default tab

  const types = Object.keys(nearbyPlaces || {});

  return (
    <div style={{ padding: '30px', fontFamily: 'Arial, sans-serif', lineHeight: 1.6 }}>
      {nearbyPlaces && (
        <>
          {/* Tabs */}
          <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
            {types.map((type) => (
              <button
                key={type}
                onClick={() => setActiveType(type)}
                style={{
                  padding: '10px 20px',
                  borderRadius: '20px',
                  border: activeType === type ? '2px solid #333' : '1px solid #ccc',
                  backgroundColor: activeType === type ? '#333' : '#f9f9f9',
                  color: activeType === type ? 'white' : 'black',
                  fontWeight: activeType === type ? 'bold' : 'normal',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                {typeIcons[type]} {type.charAt(0).toUpperCase() + type.slice(1)}
              </button>
            ))}
          </div>

          {/* Active Tab Content */}
          <div style={{
            border: '1px solid #eee',
            borderRadius: '12px',
            padding: '20px',
            backgroundColor: '#fafafa',
            boxShadow: '0 2px 6px rgba(0,0,0,0.05)'
          }}>
            <h3 style={{ marginTop: 0 }}>{typeIcons[activeType]} {activeType.charAt(0).toUpperCase() + activeType.slice(1)}</h3>

            {nearbyPlaces[activeType].length > 0 ? (
              <ul style={{ listStyle: 'none', padding: 0 }}>
                {nearbyPlaces[activeType].map((place) => (
                  <li key={place.name} style={{ marginBottom: '16px' }}>
                    <div style={{ fontWeight: 'bold', fontSize: '16px' }}>{place.name} <span style={{ color: '#888' }}>({place.rating}/5)</span></div>
                    <div style={{ fontSize: '14px', color: '#555' }}>{place.address}</div>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No {activeType}s nearby.</p>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default NearbyPlaces;
